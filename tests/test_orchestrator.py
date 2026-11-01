"""The orchestrator runs headless agent jobs in parallel, gates each on a
validator, feeds validator errors back on retry, and resumes after a restart.
A fake `claude` binary stands in for the real one."""

import asyncio
import json
import os
import stat
import textwrap
from pathlib import Path

import pytest

from pipeline.orchestrator import Job, Orchestrator

FAKE = textwrap.dedent('''\
    #!/usr/bin/env python3
    # Fake claude: writes the file named in the prompt; writes "good" only when
    # resumed (i.e. after validator feedback) if the prompt contains FAILFIRST.
    import json, sys, os, uuid
    args = sys.argv[1:]
    prompt = args[args.index("-p") + 1]
    resumed = "--resume" in args
    calls = os.environ["FAKE_LOG"]
    with open(calls, "a") as f:
        f.write(json.dumps({"prompt": prompt, "resumed": resumed, "args": args, "env_session": os.environ.get("CLAUDE_CODE_SESSION_ID"), "env_cache": os.environ.get("BOXGRAPH_CACHE")}) + "\\n")
    target = None
    for tok in prompt.split():
        if tok.startswith("TARGET="):
            target = tok.split("=", 1)[1]
    first = os.environ.get("FAKE_FIRST_PROMPT_FILE")
    content = "good"
    if "FAILFIRST" in prompt and not resumed:
        content = "bad"
    if resumed and "FAILALWAYS" in open(first).read():
        content = "bad"
    memo = os.path.join(os.path.dirname(calls), "last_target")
    if target:
        open(memo, "w").write(target)
    elif os.path.exists(memo):
        target = open(memo).read()
    if "SLOW" in prompt:
        import time
        with open(calls + ".times", "a") as f:
            f.write(f"start {target} {time.time()}\\n")
        time.sleep(0.4)
        with open(calls + ".times", "a") as f:
            f.write(f"end {target} {time.time()}\\n")
    if target:
        open(target, "w").write(content)
    sid = args[args.index("--session-id") + 1] if "--session-id" in args else args[args.index("--resume") + 1] if resumed else "sess-x"
    print(json.dumps({"type": "system", "subtype": "init", "session_id": sid}))
    if "PIDFILE" in prompt:
        open(os.path.join(os.path.dirname(calls), "agent.pid"), "w").write(str(os.getpid()))
    if "HANG" in prompt:
        import time
        time.sleep(60)
    if "CRASH" in prompt:
        sys.stderr.write("API error: overloaded\\n")
        sys.exit(1)
    if "WRITEOUT" in prompt:
        open(os.path.join(os.path.dirname(calls), "outside.txt"), "w").write("x")
    if "WRITEPNG" in prompt and target:
        open(os.path.join(os.path.dirname(target), "page5.png"), "w").write("x")
    if "HUGE" in prompt:
        print(json.dumps({"type": "user", "blob": "x" * 300000}))
    denials = [{"tool_name": "Edit", "tool_input": {"file_path": "x.yaml"}}] if "DENYEDIT" in prompt else []
    print(json.dumps({"type": "result", "subtype": "success", "session_id": sid, "total_cost_usd": 0.5,
                      "num_turns": 3, "result": "done", "is_error": False, "permission_denials": denials}))
''')

VALIDATOR = textwrap.dedent('''\
    #!/usr/bin/env python3
    import sys
    content = open(sys.argv[1]).read() if __import__("os").path.exists(sys.argv[1]) else ""
    if content == "good":
        print("SOUND"); sys.exit(0)
    print("NOT SOUND: content is " + repr(content)); sys.exit(1)
''')


@pytest.fixture
def env(tmp_path, monkeypatch):
    fake = tmp_path / "claude"
    fake.write_text(FAKE)
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    val = tmp_path / "validate.py"
    val.write_text(VALIDATOR)
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_LOG", str(log))
    (tmp_path / "first.txt").write_text("")  # each test starts from its own, empty first-prompt file
    monkeypatch.setenv("FAKE_FIRST_PROMPT_FILE", str(tmp_path / "first.txt"))
    return tmp_path, fake, val, log


def make_job(tmp, val, name, extra=""):
    target = tmp / f"{name}.txt"
    return Job(id=name, kind="read", prompt=f"TARGET={target} {extra}", cwd=str(tmp),
               validate=["python3", str(val), str(target)], max_attempts=3, budget_usd=5, max_turns=10)


def calls(log):
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def test_job_passes_first_time(env):
    """A job whose output validates passes after one attempt, with its cost recorded."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=2, logs=tmp / "logs")
    res = asyncio.run(o.run([make_job(tmp, val, "a")]))
    assert res["a"]["status"] == "passed"
    assert res["a"]["attempts"] == 1
    assert res["a"]["cost_usd"] == 0.5


def test_validator_feedback_is_sent_on_resume(env):
    """When validation fails, the agent's session is resumed with the validator's output."""
    tmp, fake, val, log = env
    os.environ["FAKE_FIRST_PROMPT_FILE"] = str(tmp / "first.txt")  # reset per test by the env fixture
    (tmp / "first.txt").write_text("")
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=2, logs=tmp / "logs")
    res = asyncio.run(o.run([make_job(tmp, val, "b", "FAILFIRST")]))
    assert res["b"]["status"] == "passed"
    assert res["b"]["attempts"] == 2
    c = calls(log)
    assert c[1]["resumed"] and "NOT SOUND" in c[1]["prompt"]


def test_job_is_parked_after_max_attempts(env):
    """A job that never validates is parked for a human after its attempts run out."""
    tmp, fake, val, log = env
    (tmp / "first.txt").write_text("FAILALWAYS")
    os.environ["FAKE_FIRST_PROMPT_FILE"] = str(tmp / "first.txt")  # reset per test by the env fixture
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=2, logs=tmp / "logs")
    res = asyncio.run(o.run([make_job(tmp, val, "c", "FAILFIRST")]))
    assert res["c"]["status"] == "parked"
    assert res["c"]["attempts"] == 3
    assert "NOT SOUND" in res["c"]["last_validation"]


def test_jobs_run_in_parallel_and_dependencies_wait(env):
    """Independent jobs run in parallel; a dependent job waits for its dependencies."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=3, logs=tmp / "logs")
    j1, j2 = make_job(tmp, val, "p1"), make_job(tmp, val, "p2")
    j3 = make_job(tmp, val, "after")
    j3.depends_on = ["p1", "p2"]
    res = asyncio.run(o.run([j3, j1, j2]))
    assert all(res[k]["status"] == "passed" for k in ("p1", "p2", "after"))
    order = [Path(next(t for t in c["prompt"].split() if t.startswith("TARGET="))).stem for c in calls(log)]
    assert order.index("after") == 2


def test_restart_skips_passed_jobs(env):
    """A restarted orchestrator does not rerun jobs that passed."""
    tmp, fake, val, log = env
    db = tmp / "state.db"
    asyncio.run(Orchestrator(db, claude_bin=str(fake), logs=tmp / "logs").run([make_job(tmp, val, "r")]))
    n = len(calls(log))
    res = asyncio.run(Orchestrator(db, claude_bin=str(fake), logs=tmp / "logs").run([make_job(tmp, val, "r")]))
    assert res["r"]["status"] == "passed"
    assert len(calls(log)) == n  # not run again


def test_command_line_restricts_tools_and_budget(env):
    """Agents run with a restricted tool set, a turn limit and a budget, and cannot delegate."""
    tmp, fake, val, log = env
    j = make_job(tmp, val, "t")
    j.allowed_tools = ["Read", "Write(records/t/**)"]
    asyncio.run(Orchestrator(tmp / "state.db", claude_bin=str(fake), logs=tmp / "logs").run([j]))
    args = calls(log)[0]["args"]
    assert "--permission-mode" in args and args[args.index("--permission-mode") + 1] == "dontAsk"
    assert "Write(records/t/**)" in args
    assert "--max-budget-usd" in args and "--max-turns" in args
    assert "Agent" in args[args.index("--disallowedTools") + 1:]


def test_a_job_can_deny_more_tools(env):
    """A job can deny tools beyond the standard list, such as reading a given directory."""
    tmp, fake, val, log = env
    j = make_job(tmp, val, "x")
    j.disallowed_tools = ["Read(//secret/**)"]
    asyncio.run(Orchestrator(tmp / "state.db", claude_bin=str(fake), logs=tmp / "logs").run([j]))
    args = calls(log)[0]["args"]
    assert "Read(//secret/**)" in args[args.index("--disallowedTools") + 1:]


def test_very_long_output_lines_do_not_crash(env):
    """Very long agent output lines do not crash the orchestrator."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), logs=tmp / "logs")
    res = asyncio.run(o.run([make_job(tmp, val, "h", "HUGE")]))
    assert res["h"]["status"] == "passed"


def test_each_job_has_its_own_session_and_a_clean_environment(env, monkeypatch):
    """Each job gets its own session id and none of the parent session's environment."""
    tmp, fake, val, log = env
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "parent-session")
    (tmp / "first.txt").write_text("")
    os.environ["FAKE_FIRST_PROMPT_FILE"] = str(tmp / "first.txt")  # reset per test by the env fixture
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), logs=tmp / "logs")
    asyncio.run(o.run([make_job(tmp, val, "s", "FAILFIRST")]))
    c = calls(log)
    assert all(x["env_session"] is None for x in c)
    first_args, second_args = c[0]["args"], c[1]["args"]
    sid = first_args[first_args.index("--session-id") + 1]
    assert sid != "parent-session"
    assert second_args[second_args.index("--resume") + 1] == sid


def test_refused_writes_are_reported_back_on_retry(env):
    """When the agent's writes were refused, the retry tells it which, and the job records them."""
    tmp, fake, val, log = env
    (tmp / "first.txt").write_text("")
    os.environ["FAKE_FIRST_PROMPT_FILE"] = str(tmp / "first.txt")  # reset per test by the env fixture
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), logs=tmp / "logs")
    res = asyncio.run(o.run([make_job(tmp, val, "d", "FAILFIRST DENYEDIT")]))
    c = calls(log)
    assert "Edit x.yaml" in c[1]["prompt"]
    assert "Edit x.yaml" in (res["d"]["error"] or "")


def test_an_interrupted_job_resumes_its_session(env):
    """A job left running when the orchestrator was stopped resumes the session named in its log."""
    tmp, fake, val, log = env
    db = tmp / "state.db"
    o = Orchestrator(db, claude_bin=str(fake), logs=tmp / "logs")
    o._put("i", kind="read", status="running", attempts=0, cost_usd=0.0, turns=0)
    (tmp / "logs").mkdir(exist_ok=True)
    (tmp / "logs" / "i.attempt1.jsonl").write_text(
        json.dumps({"type": "system", "subtype": "init", "session_id": "sess-old"}) + "\n")
    (tmp / "last_target").write_text(str(tmp / "i.txt"))  # what the interrupted run was writing
    res = asyncio.run(o.run([make_job(tmp, val, "i")]))
    assert res["i"]["status"] == "passed"
    c = calls(log)[0]
    assert c["resumed"] and c["args"][c["args"].index("--resume") + 1] == "sess-old"
    assert "interrupted" in c["prompt"]


def test_jobs_that_share_a_lock_never_overlap(env):
    """Jobs holding the same lock (two relation jobs editing one record) run one after the other; others run alongside."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=3, logs=tmp / "logs")
    a, b, c = (make_job(tmp, val, n, "SLOW") for n in ("ab", "ac", "de"))
    a.locks, b.locks, c.locks = ["a", "b"], ["c", "a"], ["d", "e"]
    res = asyncio.run(o.run([a, b, c]))
    assert all(r["status"] == "passed" for r in res.values())
    span = {}
    for line in Path(str(log) + ".times").read_text().splitlines():
        what, target, t = line.split()
        span.setdefault(Path(target).stem, {})[what] = float(t)
    first, second = sorted(("ab", "ac"), key=lambda k: span[k]["start"])
    assert span[second]["start"] >= span[first]["end"]
    assert span["de"]["start"] < span[second]["start"]  # the unlocked job did not wait


def test_a_job_whose_dependency_did_not_pass_is_blocked_not_run(env):
    """A job waits for its dependencies to pass; if one is parked, the job is blocked and its agent never starts."""
    tmp, fake, val, log = env
    (tmp / "first.txt").write_text("FAILALWAYS")
    os.environ["FAKE_FIRST_PROMPT_FILE"] = str(tmp / "first.txt")  # reset per test by the env fixture
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=2, logs=tmp / "logs")
    bad = make_job(tmp, val, "bad", "FAILFIRST")
    after = make_job(tmp, val, "after_bad")
    after.depends_on = ["bad"]
    res = asyncio.run(o.run([after, bad]))
    assert res["bad"]["status"] == "parked"
    assert res["after_bad"]["status"] == "blocked" and "bad" in res["after_bad"]["error"]
    assert not any("after_bad" in c["prompt"] for c in calls(log))


def test_a_job_environment_reaches_the_agent_and_a_hung_gate_times_out(env):
    """A job's environment variables reach its agent, and a gate that runs past its time limit fails the attempt with a message."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs")
    j = make_job(tmp, val, "envjob")
    j.env = {"BOXGRAPH_CACHE": "/shared/cache"}
    j.validate = ["python3", "-c", "import time; time.sleep(5)"]
    j.validate_timeout_s = 1
    j.max_attempts = 1
    res = asyncio.run(o.run([j]))
    assert calls(log)[0]["env_cache"] == "/shared/cache"
    assert res["envjob"]["status"] == "parked" and "timed out" in res["envjob"]["last_validation"]


def test_a_reset_job_runs_again_from_scratch(env):
    """Resetting a passed job forgets its state, so the next run starts a fresh agent for it."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs")
    asyncio.run(o.run([make_job(tmp, val, "again")]))
    o.reset(["again"])
    res = asyncio.run(o.run([make_job(tmp, val, "again")]))
    assert res["again"]["status"] == "passed"
    assert len(calls(log)) == 2 and not calls(log)[1]["resumed"]


def test_a_parked_job_stays_parked_until_it_is_reset(env):
    """A job parked for a person is not retried by later runs (nor its cost forgotten) until it is reset."""
    tmp, fake, val, log = env
    (tmp / "first.txt").write_text("FAILALWAYS")
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs")
    asyncio.run(o.run([make_job(tmp, val, "stuck", "FAILFIRST")]))
    n, cost = len(calls(log)), o._get("stuck")["cost_usd"]
    res = asyncio.run(o.run([make_job(tmp, val, "stuck", "FAILFIRST")]))
    assert res["stuck"]["status"] == "parked" and len(calls(log)) == n and res["stuck"]["cost_usd"] == cost
    o.reset(["stuck"])
    asyncio.run(o.run([make_job(tmp, val, "stuck", "FAILFIRST")]))
    assert len(calls(log)) > n


def test_the_budget_is_for_the_whole_job_not_each_attempt(env):
    """Each retry gets only what is left of the job's budget, and a job whose budget is spent stops."""
    tmp, fake, val, log = env
    (tmp / "first.txt").write_text("FAILALWAYS")
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs")
    j = make_job(tmp, val, "spend", "FAILFIRST")
    j.budget_usd, j.max_attempts = 1.0, 5  # the fake costs 0.5 a call
    res = asyncio.run(o.run([j]))
    budgets = [float(c["args"][c["args"].index("--max-budget-usd") + 1]) for c in calls(log)]
    assert budgets == [1.0, 0.5]
    assert res["spend"]["status"] == "parked" and "budget" in res["spend"]["error"]


def test_stopping_a_run_stops_its_agents(env):
    """When a run is cancelled, its agents are killed, and their jobs can be resumed by the next run."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs")

    async def go():
        task = asyncio.create_task(o.run([make_job(tmp, val, "long", "PIDFILE HANG")]))
        for _ in range(100):
            await asyncio.sleep(0.05)
            if (tmp / "agent.pid").exists():
                break
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(go())
    pid = int((tmp / "agent.pid").read_text())
    import time
    time.sleep(0.2)
    alive = os.path.exists(f"/proc/{pid}") and "zombie" not in open(f"/proc/{pid}/status").read().lower()
    assert not alive
    assert o._get("long")["status"] == "running"  # resumable


def test_a_dependency_outside_the_run_must_already_have_passed(env):
    """A job whose dependency is not in this run starts only if that dependency is known to have passed."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs")
    j = make_job(tmp, val, "needs")
    j.depends_on = ["elsewhere"]
    assert asyncio.run(o.run([j]))["needs"]["status"] == "blocked"
    assert asyncio.run(o.run([j], passed_elsewhere={"elsewhere"}))["needs"]["status"] == "passed"


def test_a_log_the_gate_requires_must_be_written_by_this_job(env):
    """A file a job must write passes its gate only if this job wrote it, not if it was left by an earlier one."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs")
    (tmp / "old_log.md").write_text("from an earlier pass")
    j = make_job(tmp, val, "fresh")
    j.max_attempts = 1
    j.fresh = [str(tmp / "old_log.md")]
    res = asyncio.run(o.run([j]))
    assert res["fresh"]["status"] == "parked" and "old_log.md" in res["fresh"]["last_validation"]


def test_writing_outside_the_jobs_area_fails_the_attempt(env):
    """An agent that writes outside the paths its job may write, by any means, fails that attempt and is told what it wrote."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs", watch=tmp)
    j = make_job(tmp, val, "stray", "WRITEOUT")
    j.max_attempts, j.writable = 1, ["stray.txt", "logs/**", "state.db*", "calls.jsonl*", "last_target", "first.txt"]
    res = asyncio.run(o.run([j]))
    assert res["stray"]["status"] == "parked" and "outside.txt" in res["stray"]["last_validation"]


def test_page_images_in_a_record_fail_the_attempt(env):
    """An image, PDF or text dump written into a record outside its ignored folders fails the attempt (papers are copyrighted)."""
    tmp, fake, val, log = env
    rec = tmp / "records" / "x"
    rec.mkdir(parents=True)
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs", watch=tmp)
    j = Job(id="png", kind="read", prompt=f"TARGET={rec / 'notes.txt'} WRITEPNG", cwd=str(tmp),
            validate=["true"], max_attempts=1, writable=["records/x/**", "logs/**", "state.db*", "calls.jsonl*",
                                                          "last_target", "first.txt"])
    res = asyncio.run(o.run([j]))
    assert res["png"]["status"] == "parked" and "page5.png" in res["png"]["last_validation"]


def test_an_agent_that_dies_without_a_result_is_reported_with_its_error(env):
    """When the agent exits without a result (an API error, an expired login), the job records why."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs")
    j = make_job(tmp, val, "dies", "CRASH")
    j.max_attempts, j.validate = 1, ["false"]
    res = asyncio.run(o.run([j]))
    assert res["dies"]["status"] == "parked" and "overloaded" in res["dies"]["error"]


def test_each_passed_job_is_reported_as_it_passes(env):
    """The run reports each job as it passes, so its record of finished work is current even if the run is killed."""
    tmp, fake, val, log = env
    seen = []
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs", on_passed=seen.append)
    asyncio.run(o.run([make_job(tmp, val, "one"), make_job(tmp, val, "two")]))
    assert sorted(r["id"] for r in seen) == ["one", "two"]


def test_copies_of_released_code_or_data_in_a_record_fail_the_attempt(tmp_path):
    """MATLAB files, .mat files and spreadsheets written into a record count as copies of a source's code or data."""
    from pipeline.orchestrator import stray_writes

    after = {"records/x/models/m/model.py": (1, 1), "records/x/cmstretchg.m": (1, 1), "records/x/kofflr.mat": (1, 1),
             "records/x/source_data.xlsx": (1, 1)}
    bad = stray_writes({}, after, ["records/x/**"])
    assert len(bad) == 3 and not any("model.py" in b for b in bad)


def test_files_changed_by_a_commit_meanwhile_are_not_blamed_on_the_agent(tmp_path):
    """A watched file that changed during an attempt but now matches the committed version (someone committed or
    checked it out) is not a stray write; an uncommitted change is."""
    import subprocess as sp

    from pipeline.orchestrator import snapshot, stray_writes

    def git(*a):
        sp.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "src.py").write_text("a = 1\n")
    (tmp_path / "other.py").write_text("b = 1\n")
    git("add", ".")
    git("commit", "-qm", "one")
    before = snapshot(tmp_path)
    import time
    time.sleep(0.01)
    (tmp_path / "src.py").write_text("a = 2\n")  # edited and committed by the operator during the attempt
    git("commit", "-qam", "two")
    (tmp_path / "other.py").write_text("b = 2\n")  # changed and not committed: a real stray write
    bad = stray_writes(before, snapshot(tmp_path), [], root=tmp_path)
    assert bad == ["other.py"]


def test_the_agent_is_never_told_to_delete_files_it_may_not_have_written(env):
    """The message about stray writes asks the agent to undo only what it wrote, never to delete files outright."""
    tmp, fake, val, log = env
    o = Orchestrator(tmp / "state.db", claude_bin=str(fake), concurrency=1, logs=tmp / "logs", watch=tmp)
    j = make_job(tmp, val, "stray2", "WRITEOUT")
    j.max_attempts, j.writable = 1, ["stray2.txt", "logs/**", "state.db*", "calls.jsonl*", "last_target", "first.txt"]
    res = asyncio.run(o.run([j]))
    msg = res["stray2"]["last_validation"]
    assert "outside.txt" in msg and "Delete them" not in msg and "did not write" in msg


def test_calls_stopped_before_reporting_their_cost_are_counted_in_tokens(tmp_path):
    """A call stopped before it reported its cost (no result in its log) is counted by the tokens in its log, each message once."""
    from pipeline.orchestrator import unreported_usage

    def msg(mid, out):
        return json.dumps({"type": "assistant", "message": {"id": mid, "usage": {
            "input_tokens": 1, "cache_creation_input_tokens": 10, "cache_read_input_tokens": 100, "output_tokens": out}}})
    (tmp_path / "read:a.attempt1.jsonl").write_text("\n".join([msg("m1", 5), msg("m1", 5), msg("m2", 7)]) + "\n")
    (tmp_path / "read:a.attempt1+.jsonl").write_text(msg("m3", 9) + "\n" + json.dumps({"type": "result", "total_cost_usd": 1.0}) + "\n")
    (tmp_path / "read:b.attempt1.jsonl").write_text(msg("m4", 100) + "\n")
    u = unreported_usage(tmp_path, "read:a")
    assert u == {"calls": 1, "input_tokens": 2, "cache_creation_input_tokens": 20, "cache_read_input_tokens": 200,
                 "output_tokens": 12}
    assert unreported_usage(tmp_path, "read:c")["calls"] == 0


def test_stopped_calls_take_each_messages_final_usage_from_the_session_transcript(tmp_path):
    """A streamed log holds a message's usage as it began; the session transcript holds it as it ended, and is used where present."""
    from pipeline.orchestrator import unreported_usage

    def ev(mid, out, sid="s1"):
        return json.dumps({"type": "assistant", "session_id": sid, "message": {"id": mid, "usage": {"output_tokens": out}}})
    logs, tr = tmp_path / "logs", tmp_path / "transcripts"
    logs.mkdir(), tr.mkdir()
    (logs / "read:a.attempt1.jsonl").write_text(ev("m1", 1) + "\n" + ev("m2", 1) + "\n")
    (tr / "s1.jsonl").write_text(ev("m1", 500) + "\n" + ev("m9", 999) + "\n")
    u = unreported_usage(logs, "read:a", transcripts=tr)
    assert u["output_tokens"] == 501 and u["calls"] == 1
