"""Run headless agent jobs in parallel, each gated by a validator.

A job is one bounded task (read one paper, audit one record, relate models)
run by the agent command (by default the `claude` CLI, as `claude -p`) in a
working directory, with a restricted tool set, a turn limit and a dollar
budget. After the agent stops, the orchestrator runs
the job's validator. If it fails, the agent's session is resumed with the
validator's output, up to max_attempts; then the job is parked for a human.
A job whose dependency did not pass is blocked and never started.
The agent's own words are never trusted; only the files and the validator.

State lives in SQLite, so a restarted orchestrator skips jobs that passed.
"""

from __future__ import annotations

import asyncio
import fnmatch
import json
import os
import re
import signal
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

DISALLOWED = ["Agent", "WebFetch", "WebSearch", "NotebookEdit"]

# Variables that tie a process to the agent session that started the run. A child agent
# must not inherit them, or it would share the parent's session identity.
PARENT_SESSION_VARS = ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_REMOTE_SESSION_ID", "CLAUDE_CODE_REMOTE_SDK_URL",
                       "CLAUDE_CODE_MESSAGING_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_PID",
                       "CLAUDE_CODE_TEE_SDK_STDOUT", "CLAUDE_CODE_CHILD_SESSION", "CLAUDECODE")
STREAM_LIMIT = 64 * 1024 * 1024


def child_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k not in PARENT_SESSION_VARS}


@dataclass
class Job:
    id: str
    kind: str
    prompt: str
    cwd: str
    validate: list[str]  # command; exit 0 = pass
    allowed_tools: list[str] = field(default_factory=lambda: ["Read", "Glob", "Grep"])
    append_system_prompt_file: str | None = None
    model: str | None = None
    max_turns: int = 200
    budget_usd: float = 30.0
    max_attempts: int = 3
    depends_on: list[str] = field(default_factory=list)
    timeout_s: int = 8 * 3600  # the agent, including its own checks; a model run alone may take two hours
    disallowed_tools: list[str] = field(default_factory=list)  # in addition to DISALLOWED
    locks: list[str] = field(default_factory=list)  # jobs sharing a lock never run at the same time
    env: dict[str, str] = field(default_factory=dict)  # extra environment for the agent and its gate
    validate_timeout_s: int = 6 * 3600  # a gate that runs longer fails the attempt (it may run several long models)
    fresh: list[str] = field(default_factory=list)  # files the job must (re)write; one left from before fails it
    writable: list[str] = field(default_factory=list)  # globs (relative to the watched root) the job may change


SCHEMA = """
create table if not exists jobs(
  id text primary key, kind text, status text, attempts integer, cost_usd real, turns integer,
  session_id text, last_validation text, started real, finished real, error text)
"""


# Folders never scanned for stray writes: large, ignored by git, or the run's own.
UNWATCHED = {".git", ".venv", "__pycache__", "corpus", "build", "pipeline_state", "node_modules", ".claude",
             ".pytest_cache", ".ruff_cache"}
RECORD_IGNORED = {"text", "pages", "figwork"}  # a record's git-ignored folders, where page content may live
PAPER_CONTENT = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".gif", ".bmp", ".webp", ".txt", ".djvu",
                 ".m", ".mat", ".xlsx", ".xls"}  # pages, and copies of a source's released code or data


def _record_depth(parts: tuple[str, ...] | list[str]) -> int | None:
    """How many path parts lead to a records folder: 1 for records/, 3 for corpora/<name>/records/; None elsewhere."""
    if tuple(parts[:1]) == ("records",):
        return 1
    if len(parts) >= 3 and parts[0] == "corpora" and parts[2] == "records":
        return 3
    return None


def snapshot(root: Path) -> dict[str, tuple[int, int]]:
    """Every watched file under root, with its size and modification time."""
    out = {}
    root = Path(root)
    for dirpath, dirs, files in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        parts = rel.parts
        k = _record_depth(parts)
        dirs[:] = [d for d in dirs if d not in UNWATCHED
                   and not (k is not None and len(parts) == k + 1 and d in RECORD_IGNORED)]
        for f in files:
            fp = Path(dirpath) / f
            try:
                st = fp.stat()
            except OSError:
                continue
            out[(rel / f).as_posix()] = (st.st_size, st.st_mtime_ns)
    return out


def _git_ignored(root: Path, paths: list[str]) -> set[str]:
    """Of these paths, those git ignores (they never match a committed version, so they are kept)."""
    import subprocess

    try:
        r = subprocess.run(["git", "-C", str(root), "check-ignore", "--stdin", "-z"], input="\0".join(paths),
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return set()
    return {p for p in r.stdout.split("\0") if p}


def _differs_from_git(root: Path, paths: list[str]) -> set[str] | None:
    """Of these paths, those whose contents differ from the committed version (modified or untracked),
    or None if root is not a git checkout."""
    import subprocess

    if not paths:
        return set()
    try:
        r = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "-z", "--untracked-files=all", "--", *paths],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return {e[3:] for e in r.stdout.split("\0") if len(e) > 3}


def stray_writes(before: dict, after: dict, writable: list[str], root: Path | None = None) -> list[str]:
    """Files changed or added between two snapshots that no glob allows, or that put page content
    (an image, a PDF, a text dump) into a record outside its git-ignored folders. In a git checkout, a
    file that now matches its committed version is left out: a commit or checkout made it, not an agent."""
    changed = [p for p in sorted(after) if before.get(p) != after[p]]
    if root is not None and changed:
        differs = _differs_from_git(root, changed)
        if differs is not None:
            ignored = _git_ignored(root, changed)
            changed = [p for p in changed if p in differs or p in ignored]
    bad = []
    for path in changed:
        parts = path.split("/")
        k = _record_depth(parts)
        if k is not None and len(parts) > k + 1 and Path(path).suffix.lower() in PAPER_CONTENT:
            bad.append(f"{path} (page content, or a copy of released code or data, may not be written into a record)")
        elif not any(fnmatch.fnmatchcase(path, g.replace("**", "*")) for g in writable):
            bad.append(path)
    return bad


USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def transcript_dir(cwd: str | Path) -> Path:
    """Where the default agent command keeps the session transcripts of agents started in cwd."""
    return Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(Path(cwd).resolve()))


def _assistant_usage(lines) -> tuple[dict, str | None, bool]:
    usage, sid, ended = {}, None, False
    for line in lines:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        sid = ev.get("session_id", sid) if isinstance(ev, dict) else sid
        if not isinstance(ev, dict):
            continue
        if ev.get("type") == "result":
            ended = True
        m = ev.get("message") if ev.get("type") == "assistant" else None
        if isinstance(m, dict) and m.get("id") and isinstance(m.get("usage"), dict):
            usage[m["id"]] = m["usage"]
    return usage, sid, ended


def unreported_usage(logs: Path, job_id: str, transcripts: Path | None = None) -> dict:
    """Tokens used by a job's calls that stopped before reporting their cost (a call's log with no result
    event: stopped at a time limit, or crashed), each message counted once. A streamed log holds a message's
    usage as it began; the session transcript (in `transcripts`, where present) holds it as it ended. Their
    cost is unknown, so it is reported as tokens rather than guessed."""
    out = {"calls": 0, **{k: 0 for k in USAGE_KEYS}}
    for log in sorted(Path(logs).glob(f"{job_id}.attempt*.jsonl")):
        usage, sid, ended = _assistant_usage(log.read_text(errors="replace").splitlines())
        if ended or not usage:
            continue
        tr = Path(transcripts) / f"{sid}.jsonl" if transcripts and sid else None
        if tr is not None and tr.exists():
            final, _, _ = _assistant_usage(tr.read_text(errors="replace").splitlines())
            usage = {mid: final.get(mid, u) for mid, u in usage.items()}
        out["calls"] += 1
        for u in usage.values():
            for k in USAGE_KEYS:
                out[k] += int(u.get(k) or 0)
    return out


def _stop(proc) -> None:
    """Kill an agent and every process it started (it runs in its own process group)."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            proc.kill()
        except ProcessLookupError:
            pass


class Orchestrator:
    def __init__(self, db: Path, agent_bin: str = "claude", concurrency: int = 3, logs: Path | None = None,
                 watch: Path | None = None, on_passed=None, crash_backoff_s: float = 60.0):
        self.watch = Path(watch) if watch else None  # root scanned for writes outside a job's area
        self.on_passed = on_passed  # called with each job's row as it passes
        self.crash_backoff_s = crash_backoff_s
        self.db = Path(db)
        self.db.parent.mkdir(parents=True, exist_ok=True)
        self.agent = agent_bin
        self.concurrency = concurrency
        self.logs = Path(logs or self.db.parent / "logs")
        self.logs.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db) as c:
            c.execute(SCHEMA)

    # ---- state --------------------------------------------------------------
    def _get(self, jid: str) -> dict | None:
        with sqlite3.connect(self.db) as c:
            c.row_factory = sqlite3.Row
            r = c.execute("select * from jobs where id=?", (jid,)).fetchone()
            return dict(r) if r else None

    def _put(self, jid: str, **kw):
        cur = self._get(jid) or {"id": jid}
        cur.update(kw)
        cols = ["id", "kind", "status", "attempts", "cost_usd", "turns", "session_id", "last_validation",
                "started", "finished", "error"]
        vals = [cur.get(k) for k in cols]
        with sqlite3.connect(self.db) as c:
            c.execute(f"insert or replace into jobs({','.join(cols)}) values({','.join('?' * len(cols))})", vals)

    def status(self) -> list[dict]:
        with sqlite3.connect(self.db) as c:
            c.row_factory = sqlite3.Row
            return [dict(r) for r in c.execute("select * from jobs order by id")]

    # ---- one agent call ---------------------------------------------------------
    def _argv(self, job: Job, prompt: str, resume: str | None, budget: float | None = None) -> list[str]:
        a = [self.agent, "-p", prompt, "--output-format", "stream-json", "--verbose",
             "--permission-mode", "dontAsk", "--max-turns", str(job.max_turns),
             "--max-budget-usd", f"{job.budget_usd if budget is None else budget:g}", "--allowedTools", *job.allowed_tools,
             "--disallowedTools", *DISALLOWED, *job.disallowed_tools]
        if job.model:
            a += ["--model", job.model]
        if job.append_system_prompt_file:
            a += ["--append-system-prompt-file", job.append_system_prompt_file]
        if resume:
            a += ["--resume", resume]
        else:
            a += ["--session-id", str(uuid.uuid4())]
        return a

    async def _call(self, job: Job, prompt: str, resume: str | None, attempt: int, budget: float | None = None) -> dict:
        log = self.logs / f"{job.id}.attempt{attempt}.jsonl"
        while log.exists():  # never overwrite the log of an earlier, interrupted call
            log = log.with_name(log.stem + "+" + log.suffix)
        proc = await asyncio.create_subprocess_exec(
            *self._argv(job, prompt, resume, budget), cwd=job.cwd, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.DEVNULL, env=child_env() | job.env,
            limit=STREAM_LIMIT, start_new_session=True)  # its own process group, so all its children can be stopped
        result: dict = {}
        session = None
        with log.open("w") as f:
            async def pump():
                nonlocal result, session
                async for line in proc.stdout:
                    f.write(line.decode(errors="replace"))
                    f.flush()
                    try:
                        ev = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    session = ev.get("session_id", session)
                    if ev.get("type") == "result":
                        result = ev
            try:
                await asyncio.wait_for(asyncio.gather(pump(), proc.wait()), timeout=job.timeout_s)
            except TimeoutError:
                _stop(proc)
                result = {"is_error": True, "subtype": "timeout"}
            except BaseException:  # cancelled or failed: never leave the agent (or what it started) running
                _stop(proc)
                raise
        err = (await proc.stderr.read()).decode(errors="replace")[-2000:] if proc.stderr else ""
        if not result:  # the agent exited without its result: an API error, an expired login, a crash
            result = {"is_error": True, "subtype": "no_result", "_crashed": True,
                      "_why": f"the agent exited (code {proc.returncode}) without a result: " + (err.strip()[-500:] or "no message")}
        result.setdefault("session_id", session)
        result["_stderr"] = err
        return result

    def _last_session(self, job_id: str) -> str | None:
        """The session id in the newest log of a job, if any."""
        logs = sorted(self.logs.glob(f"{job_id}.attempt*.jsonl"), key=lambda p: p.stat().st_mtime)
        for log in reversed(logs):
            for line in log.read_text(errors="replace").splitlines()[:50]:
                try:
                    sid = json.loads(line).get("session_id")
                except (json.JSONDecodeError, AttributeError):
                    continue
                if sid:
                    return sid
        return None

    async def _validate(self, job: Job) -> tuple[bool, str]:
        proc = await asyncio.create_subprocess_exec(*job.validate, cwd=job.cwd, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.STDOUT, env=child_env() | job.env,
                                                    start_new_session=True)  # its own process group, like an agent
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=job.validate_timeout_s)
        except TimeoutError:
            _stop(proc)
            await proc.wait()
            return False, (f"The gate timed out after {job.validate_timeout_s} s. Something in the record takes too long "
                           "to run: shorten the slowest runs (fewer replicates or a shorter simulated time) and say so.")
        except BaseException:  # cancelled (a stopped run, SIGTERM): never leave the gate, or what it started, running
            _stop(proc)
            raise
        return proc.returncode == 0, out.decode(errors="replace")[-6000:]

    def reset(self, job_ids) -> None:
        """Forget these jobs' state, so the next run starts each with a fresh agent."""
        with sqlite3.connect(self.db) as c:
            c.executemany("delete from jobs where id=?", [(j,) for j in job_ids])

    # ---- a job, with retries -----------------------------------------------------
    async def _run_job(self, job: Job, sem: asyncio.Semaphore, writable: list[str]):
        prev = self._get(job.id)
        if prev and prev["status"] in ("passed", "parked"):
            return  # a parked job waits for a person: it runs again only after `reset`
        async with sem:
            session, cost, turns = None, 0.0, 0
            prompt = job.prompt
            started = time.time()
            if prev and prev["status"] == "running":
                # stopped mid-run: carry on in the same session, from what it already did
                session = self._last_session(job.id)
                cost, turns = float(prev["cost_usd"] or 0), int(prev["turns"] or 0)
                started = prev["started"] or started  # what it wrote before it was stopped is its own
                if session:
                    prompt = ("You were interrupted before you finished. Continue the task where you left off; "
                              "check what you have already written before changing it.")
            self._put(job.id, kind=job.kind, status="running", attempts=0, cost_usd=cost, turns=turns, started=started)
            all_refused: set[str] = set()
            error = None
            for attempt in range(1, job.max_attempts + 1):
                left = job.budget_usd - cost
                if left <= 0.01:
                    error = f"the job's budget of ${job.budget_usd:g} is spent (${cost:.2f})"
                    break
                before = snapshot(self.watch) if self.watch else None
                res = await self._call(job, prompt, session, attempt, budget=round(left, 2))
                session = res.get("session_id") or session
                cost += float(res.get("total_cost_usd") or 0)
                turns += int(res.get("num_turns") or 0)
                ok, out = await self._validate(job)
                stray = stray_writes(before, snapshot(self.watch), writable, root=self.watch) if self.watch else []
                stale = [f for f in job.fresh if not Path(job.cwd, f).exists() or Path(job.cwd, f).stat().st_mtime < started]
                if stray:
                    ok = False
                    out = ("These files changed outside what this job may write: " + ", ".join(stray)
                           + ". If you wrote or changed any of them, undo exactly that and keep your work inside your own "
                           "record. If you did not write a file, do not touch it: say so in one line, and it is left "
                           "for a person to look at. Then run the validator again.\n\n" + out)
                if stale:
                    ok = False
                    out = ("This job must write " + ", ".join(stale) + " itself; what is there was left by an earlier "
                           "job (or is missing).\n\n" + out)
                refused = sorted({f"{d.get('tool_name')} {(d.get('tool_input') or {}).get('file_path', '')}".strip()
                                  for d in res.get("permission_denials") or []
                                  if d.get("tool_name") in ("Write", "Edit")})
                all_refused.update(refused)
                error = res.get("_why") or (res.get("subtype") if res.get("is_error") else None)
                if res.get("is_error"):
                    # the agent stopped on an error: whatever the gate says, the job was not done
                    ok = False
                    error = res.get("_why") or res.get("api_error") or res.get("result") or res.get("subtype")
                    if res.get("api_error") == "usage_limit_reached" or res.get("api_error_status") == 429:
                        error = f"the agent stopped: {res.get('result') or res.get('api_error')}"
                        self._put(job.id, attempts=attempt, cost_usd=cost, turns=turns, session_id=session,
                                  last_validation=out, error=error)
                        break  # a usage limit is not fixed by trying again now
                if ok:
                    error = None  # an earlier failure no longer applies; refused writes are kept as a record
                if all_refused:
                    error = "; ".join(filter(None, [error, "refused writes: " + ", ".join(sorted(all_refused))]))
                self._put(job.id, attempts=attempt, cost_usd=cost, turns=turns, session_id=session,
                          last_validation=out, error=error)
                if ok:
                    self._put(job.id, status="passed", finished=time.time())
                    if self.on_passed:
                        self.on_passed(self._get(job.id))
                    return
                if res.get("_crashed") or res.get("is_error"):
                    if attempt < job.max_attempts:
                        await asyncio.sleep(self.crash_backoff_s * attempt)  # an outage: wait before trying again
                    prompt = ("You were interrupted before you finished. Continue the task where you left off; "
                              "check what you have already written before changing it.")
                    continue
                prompt = ("The validator still reports problems. Fix every ERROR below, then run the validator "
                          "again yourself and stop only when it reports SOUND.\n\n" + out)
                if refused:
                    prompt += ("\n\nThese writes were refused by the permission rules: " + ", ".join(refused)
                               + ". Use a path inside the directories you are allowed to write, given relative to "
                               "the project root, and try again.")
            self._put(job.id, status="parked", finished=time.time(), error=error or "the gate still fails; see last_validation")

    async def run(self, jobs: list[Job], passed_elsewhere: set[str] | frozenset = frozenset()) -> dict[str, dict]:
        """Run the jobs. A dependency not among them must be in passed_elsewhere (e.g. the ledger) or have
        passed on this machine. A SIGTERM stops the run, and its agents, as an interrupt does."""
        sem = asyncio.Semaphore(self.concurrency)
        done: dict[str, asyncio.Event] = {j.id: asyncio.Event() for j in jobs}
        own = ["logs/**", "*.db", "*.db-journal"]  # the orchestrator's own files, if they are under the watched root
        writable = sorted({g for j in jobs for g in j.writable} | set(own))
        main = asyncio.current_task()
        loop = asyncio.get_running_loop()
        try:
            loop.add_signal_handler(signal.SIGTERM, main.cancel)
        except (NotImplementedError, RuntimeError, ValueError):
            pass

        locks = {name: asyncio.Lock() for j in jobs for name in j.locks}

        async def guarded(j: Job):
            held: list[asyncio.Lock] = []
            try:
                for d in j.depends_on:
                    if d in done:
                        await done[d].wait()
                failed = [d for d in j.depends_on
                          if (self._get(d) or {}).get("status") != "passed" and not (d not in done and d in passed_elsewhere)]
                if failed:  # never build on a step that did not pass its gate
                    self._put(j.id, kind=j.kind, status="blocked", attempts=0, cost_usd=0.0, turns=0,
                              error="waits for " + ", ".join(failed) + ", which did not pass", finished=time.time())
                    return
                for name in sorted(set(j.locks)):  # one global order, so two jobs never deadlock
                    await locks[name].acquire()
                    held.append(locks[name])
                await self._run_job(j, sem, writable)
            finally:
                for lk in reversed(held):
                    lk.release()
                done[j.id].set()

        try:
            await asyncio.gather(*(guarded(j) for j in jobs))
        finally:
            try:
                loop.remove_signal_handler(signal.SIGTERM)
            except (NotImplementedError, RuntimeError, ValueError):
                pass
        return {r["id"]: r for r in self.status() if r["id"] in done}
