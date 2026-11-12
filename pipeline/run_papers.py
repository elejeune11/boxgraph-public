"""Read the corpus into records with parallel headless agents.

  python -m pipeline.run_papers --corpus motor_clutch --plan     # what would run, with budget caps
  python -m pipeline.run_papers --corpus motor_clutch [--papers a,b] [--stages ...] [--concurrency 3]

Stages: ingest (code) -> read -> audit -> digitize (one agent per paper and
stage, papers in parallel; released code or data is only read) -> relate
(one agent per pair of records that show a sign of a relation, see
pipeline/pairs.py) -> validate (one agent per related pair: each one's models
against the other's measurements) -> build (code). Every agent job is gated
by `boxgraph validate`. Validate jobs share the --budget-relate cap.

--corpus <name> names the corpus: its list, ledger, overview text and records
are in corpora/<name>/, its sources in corpus/<name>/, its build in
build/<name>/ and its state (and agent transcripts) in pipeline_state/<name>/;
see pipeline.corpus.layout. Jobs that passed are listed in the corpus's
completed.yaml, committed with the records, and are not run again (unless
--rerun). Progress within a run is kept in its state folder, so an interrupted
run resumes where it stopped.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import os
import subprocess
import sys
import time
from pathlib import Path

from boxgraph.ingest import ingest
from pipeline.corpus import check_papers, forget_completed, layout, load_completed, load_papers, missing_sources, record_completed
from pipeline.orchestrator import USAGE_KEYS, Job, Orchestrator, transcript_dir, unreported_usage
from pipeline.pairs import candidate_pairs, split_pairs

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "pipeline" / "prompts"
VENV = ".venv/bin"
PAPERS = ROOT / "pipeline" / "papers.yaml"
LEDGER = ROOT / "pipeline" / "completed.yaml"
CACHE = "build/cache"  # shared by every gate, build and corpus (keyed by code and inputs), so a retry does not rerun every simulation
RECORDS = "records"  # where the corpus's records are, relative to ROOT; use_corpus points these at a named corpus
BUILD = "build"
STATE = "pipeline_state"
OVERVIEW = "overview/content.yaml"  # the overview's words, relative to ROOT
PER_PAPER = ("read", "audit", "digitize")


def papers() -> list[dict]:
    return load_papers(PAPERS)


def use_corpus(name: str | None) -> None:
    """Point the pipeline at a corpus: the default one (None), or corpora/<name>/ (see pipeline.corpus.layout)."""
    global PAPERS, LEDGER, OVERVIEW, RECORDS, BUILD, STATE
    lay = layout(ROOT, name)
    PAPERS, LEDGER, OVERVIEW = lay.papers, lay.ledger, lay.overview.relative_to(ROOT).as_posix()
    RECORDS, BUILD, STATE = lay.records, lay.build, lay.state


def stages_of(entry: dict) -> tuple[str, ...]:
    """The per-entry stages: a paper is read, audited and digitized; released code or data is read."""
    return ("read",) if entry.get("kind") in ("software", "dataset") else PER_PAPER


READ_ONLY_SHELL = ["Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(wc:*)", "Bash(grep:*)",
                   "Bash(pdftotext:*)"]  # no sed: its w command writes files; agents read with the Read tool


def write_rules(rel: str) -> list[str]:
    """Write and Edit for a path under the project, in both the project-relative
    form and the absolute (//) form, so whichever path an agent uses matches."""
    absolute = "/" + str(ROOT / rel)
    return [f"Write({rel})", f"Edit({rel})", f"Write({absolute})", f"Edit({absolute})"]


def reader_tools(rid: str) -> list[str]:
    return ["Read", "Glob", "Grep", *write_rules(f"{RECORDS}/{rid}/**"),
            f"Bash({VENV}/boxgraph validate:*)", f"Bash({VENV}/python:*)", *READ_ONLY_SHELL]


def _validate(rid: str) -> str:
    return f"{VENV}/boxgraph validate {RECORDS}/{rid} --cache {CACHE}"


def _gate_with_log(rid: str, log: str, why: str) -> list[str]:
    return ["sh", "-c", f"{_validate(rid)} && "
            f"{{ test -s {RECORDS}/{rid}/{log} || {{ echo 'ERROR: {RECORDS}/{rid}/{log} was not written; {why}'; exit 1; }}; }}"]


def _with_extra(js: list[Job], extra: str) -> list[Job]:
    for j in js:
        j.env = {**j.env, "BOXGRAPH_CACHE": str(ROOT / CACHE)}  # the agent's own validate shares its gate's cache
        # the run writes the ledger as each job passes: never another job's stray write
        if LEDGER.is_relative_to(ROOT):
            j.writable = sorted({*j.writable, LEDGER.relative_to(ROOT).as_posix()})
        if extra:
            j.prompt = j.prompt.rstrip() + "\n\n" + extra.strip() + "\n"
    return js


def jobs(model: str, budget_read: float, budget_audit: float, budget_relate: float, extra: str = "",
         budget_digitize: float | None = None) -> dict[str, list[Job]]:
    """The per-paper jobs: read, then audit, then digitize, for every paper in the corpus list.
    (Relation jobs depend on which records exist; see relate_jobs.)"""
    ps = papers()
    ids = [p["id"] for p in ps]
    today = dt.date.today().isoformat()
    guide = str(PROMPTS / "record_guide.md")
    out: dict[str, list[Job]] = {"read": [], "audit": [], "digitize": []}
    for p in ps:
        mine = [f"{RECORDS}/{p['id']}/**"]
        if p.get("kind") in ("software", "dataset"):  # a paper's released code or data: one reading job
            prompt = "read_code.md" if p["kind"] == "software" else "read_data.md"
            fmt = dict(id=p["id"], records=RECORDS, file=p["file"], papers=", ".join(p.get("papers") or []), page_note=p.get("note", ""))
            out["read"].append(Job(
                id=f"read:{p['id']}", kind="read", prompt=(PROMPTS / prompt).read_text().format(**fmt), cwd=str(ROOT),
                validate=["sh", "-c", _validate(p["id"])],
                allowed_tools=[*reader_tools(p["id"]), f"Bash({VENV}/boxgraph digest:*)"],
                append_system_prompt_file=guide, model=model, max_turns=400, budget_usd=budget_read, max_attempts=3,
                depends_on=[f"read:{x}" for x in p.get("papers") or []], writable=mine))
            continue
        fmt = dict(id=p["id"], records=RECORDS, file=p["file"], first=p["pages"][0], last=p["pages"][1], page_note=p.get("note", ""),
                   others=", ".join(i for i in ids if i != p["id"]) or "none", date=today, model=model)
        out["read"].append(Job(
            id=f"read:{p['id']}", kind="read", prompt=(PROMPTS / "read.md").read_text().format(**fmt), cwd=str(ROOT),
            validate=["sh", "-c", _validate(p["id"])], allowed_tools=reader_tools(p["id"]),
            append_system_prompt_file=guide, model=model, max_turns=400, budget_usd=budget_read, max_attempts=3,
            writable=mine))
        out["audit"].append(Job(
            id=f"audit:{p['id']}", kind="audit", prompt=(PROMPTS / "audit.md").read_text().format(**fmt), cwd=str(ROOT),
            validate=_gate_with_log(p["id"], "audit.md", "the audit must log its changes and disagreements there"),
            allowed_tools=reader_tools(p["id"]), append_system_prompt_file=guide, model=model,
            max_turns=300, budget_usd=budget_audit, max_attempts=2, depends_on=[f"read:{p['id']}"],
            writable=mine, fresh=[f"{RECORDS}/{p['id']}/audit.md"]))
        out["digitize"].append(Job(
            id=f"digitize:{p['id']}", kind="digitize", prompt=(PROMPTS / "digitize.md").read_text().format(**fmt),
            cwd=str(ROOT), validate=_gate_with_log(p["id"], "figures.md", "log every figure read, checked or left out there"),
            allowed_tools=[*reader_tools(p["id"]), f"Bash({VENV}/boxgraph figure:*)", "Bash(pdftoppm:*)", "Bash(mkdir:*)"],
            append_system_prompt_file=guide, model=model, max_turns=400,
            budget_usd=budget_audit if budget_digitize is None else budget_digitize, max_attempts=2,
            depends_on=[f"audit:{p['id']}"], writable=mine, fresh=[f"{RECORDS}/{p['id']}/figures.md"]))
    for js in out.values():
        _with_extra(js, extra)
    return out


def relate_jobs(pairs: dict[tuple[str, str], list[str]], model: str, budget: float, extra: str = "") -> list[Job]:
    """One relation job per pair of records. Each may edit only its two records' relations, questions,
    quantities and models, and holds a lock on both, so two jobs never edit one record at once."""
    guide = str(PROMPTS / "record_guide.md")
    out = []
    for (a, b), reasons in sorted(pairs.items()):
        check = f"{BUILD}/relate-check/{a}+{b}"
        tools = ["Read", "Glob", "Grep", f"Bash({VENV}/boxgraph validate:*)", f"Bash({VENV}/boxgraph relations:*)",
                 f"Bash({VENV}/python:*)", *READ_ONLY_SHELL, *write_rules(f"{check}/**")]
        writable = [f"{check}/**"]
        for rid in (a, b):
            for f in ("relations.yaml", "questions.yaml", "quantities.yaml", "cited.yaml", "models/**"):
                tools += write_rules(f"{RECORDS}/{rid}/{f}")
                writable.append(f"{RECORDS}/{rid}/{f}")
        prompt = (PROMPTS / "relate.md").read_text().format(
            a=a, b=b, records=RECORDS, reasons="\n".join(f"- {r}" for r in reasons), check=check)
        # the job may touch models, so both records are validated with their models run (from the shared cache)
        gate = ["sh", "-c", f"{VENV}/boxgraph validate {RECORDS}/{a} {RECORDS}/{b} --cache {CACHE} && "
                f"{VENV}/boxgraph relations {RECORDS} --only {a},{b}"]
        out.append(Job(id=f"relate:{a}+{b}", kind="relate", prompt=prompt, cwd=str(ROOT), validate=gate,
                       allowed_tools=tools, append_system_prompt_file=guide, model=model, max_turns=200,
                       budget_usd=budget, max_attempts=2, locks=[a, b], writable=writable))
    return _with_extra(out, extra)


def validate_jobs(pairs: dict[tuple[str, str], list[str]], model: str, budget: float, extra: str = "") -> list[Job]:
    """One validation job per pair of records: the models of each judged against the other's measurements.
    Each may write only its two records' validations, added inputs and questions, and locks both."""
    guide = str(PROMPTS / "record_guide.md")
    out = []
    for (a, b), reasons in sorted(pairs.items()):
        check = f"{BUILD}/validate-check/{a}+{b}"
        tools = ["Read", "Glob", "Grep", f"Bash({VENV}/boxgraph validate:*)", f"Bash({VENV}/boxgraph validations:*)",
                 f"Bash({VENV}/python:*)", *READ_ONLY_SHELL, *write_rules(f"{check}/**")]
        writable = [f"{check}/**"]
        for rid in (a, b):
            for f in ("validations.yaml", "added.yaml", "questions.yaml"):
                tools += write_rules(f"{RECORDS}/{rid}/{f}")
                writable.append(f"{RECORDS}/{rid}/{f}")
        prompt = (PROMPTS / "validate.md").read_text().format(
            a=a, b=b, records=RECORDS, reasons="\n".join(f"- {r}" for r in reasons), check=check, venv=VENV)
        gate = ["sh", "-c", f"{VENV}/boxgraph validate {RECORDS}/{a} {RECORDS}/{b} --cache {CACHE} && "
                f"{VENV}/boxgraph validations {RECORDS} --only {a},{b} --cache {CACHE}"]
        out.append(Job(id=f"validate:{a}+{b}", kind="validate", prompt=prompt, cwd=str(ROOT), validate=gate,
                       allowed_tools=tools, append_system_prompt_file=guide, model=model, max_turns=200,
                       budget_usd=budget, max_attempts=2, locks=[a, b], writable=writable))
    return _with_extra(out, extra)


def _paper_ids(job: Job) -> list[str]:
    return job.id.split(":", 1)[1].split("+")


def select(js: dict[str, list[Job]], stages: list[str], only: list[str] | None,
           job_ids: list[str] | None = None) -> list[Job]:
    """The jobs of the chosen stages, for the chosen papers (all if `only` is None); a relation job
    is kept when either of its papers is chosen. `job_ids`, if given, keeps only those jobs."""
    out = [j for s in (*PER_PAPER, "relate", "validate") if s in stages for j in js.get(s, [])]
    if only is not None:
        out = [j for j in out if set(_paper_ids(j)) & set(only)]
    if job_ids is not None:
        out = [j for j in out if j.id in job_ids]
    return out


def pending(js: list[Job], done: dict[str, dict], rerun: bool = False) -> list[Job]:
    """The jobs still to run: those not in the ledger, or all of them on a rerun."""
    return list(js) if rerun else [j for j in js if j.id not in done]


def plan(js: list[Job], done: dict[str, dict], rerun: bool = False) -> list[str]:
    """One line per job, done or to run with its budget cap, and the total cap."""
    todo = {j.id for j in pending(js, done, rerun)}
    lines = []
    for j in js:
        if j.id in todo:
            lines.append(f"  {j.id:36} to run    budget cap ${j.budget_usd:.0f}")
        else:
            d = done[j.id]
            cost = f"${float(d['cost_usd']):.2f}" if d.get("cost_usd") is not None else "cost not recorded"
            lines.append(f"  {j.id:36} done {d.get('date', '?')}  {cost}")
    cap = sum(j.budget_usd for j in js if j.id in todo)
    lines.append(f"  {len(todo)} job(s) to run, at most ${cap:.0f} in all (typical runs cost a third to a half of the cap)")
    return lines


def _ingest_needed(p: dict) -> bool:
    import hashlib
    import json

    d = ROOT / RECORDS / p["id"]
    meta = d / "ingest.json"
    if not meta.exists() or not (d / "text").is_dir() or not (d / "pages").is_dir():
        return True
    m = json.loads(meta.read_text())
    sha = hashlib.sha256((ROOT / p["file"]).read_bytes()).hexdigest()
    return m.get("sha256") != sha or list(m.get("page_range") or []) != list(p["pages"])


def _ledger_rows(res: dict[str, dict]) -> list[dict]:
    today = dt.date.today().isoformat()
    return [{"job": jid, "date": today, "cost_usd": round(float(r["cost_usd"] or 0), 2), "turns": int(r["turns"] or 0)}
            for jid, r in sorted(res.items()) if r["status"] == "passed"]


def _record_passed(row: dict) -> None:
    """Called as each job passes, so the ledger is current even if the run is killed."""
    record_completed(LEDGER, _ledger_rows({row["id"]: row}))


def _run(o: Orchestrator, todo: list[Job], done: dict | None = None) -> dict[str, dict]:
    res = asyncio.run(o.run(todo, passed_elsewhere=set(done or {})))
    for jid, r in sorted(res.items()):
        why = f"  ({r.get('error')})" if r["status"] != "passed" and r.get("error") else ""
        print(f"{jid:36} {r['status']:8} attempts {r['attempts']}  ${r['cost_usd'] or 0:.2f}  turns {r['turns']}{why}",
              flush=True)
    record_completed(LEDGER, _ledger_rows(res))
    return res


def _stale_rows(done: dict, pid: str) -> list[str]:
    """Ledger jobs that read a paper's old file: its own jobs and every relation or validation job it is part of."""
    return [j for j in done
            if j.split(":", 1)[1] == pid or (j.startswith(("relate:", "validate:")) and pid in _paper_ids_of(j))]


def _paper_ids_of(job_id: str) -> list[str]:
    return job_id.split(":", 1)[1].split("+")


def _tokens(u: dict) -> str:
    return (f"{u['output_tokens']:,} output, {u['input_tokens'] + u['cache_creation_input_tokens']:,} input, "
            f"{u['cache_read_input_tokens']:,} cached input tokens")


def _build(title: str) -> int:
    content = ["--overview", OVERVIEW] if (ROOT / OVERVIEW).exists() else []
    return subprocess.run([str(ROOT / VENV / "boxgraph"), "build", RECORDS, "--out", BUILD, "--cache", CACHE, "--save-readings", "--title", title,
                           *content],
                          cwd=ROOT, check=False).returncode


def _lock(state: Path):
    """Hold the run lock for this state folder, or return None if another run holds it."""
    import fcntl

    state.mkdir(parents=True, exist_ok=True)
    f = open(state / "run.lock", "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    return f


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stages", default="ingest,read,audit,digitize,relate,validate,build")
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--agent", default=os.environ.get("BOXGRAPH_AGENT", "claude"),
                    help="the agent command to run jobs with (default: $BOXGRAPH_AGENT or claude)")
    ap.add_argument("--model", help="the agents' model (default: the agent command's own default)")
    ap.add_argument("--budget-read", type=float, default=40)
    ap.add_argument("--budget-audit", type=float, default=20)
    ap.add_argument("--budget-digitize", type=float, default=30)
    ap.add_argument("--budget-relate", type=float, default=15)
    ap.add_argument("--corpus", required=True, help="the corpus, kept in corpora/<name>/")
    ap.add_argument("--state", help="this machine's run state (default: pipeline_state/, or pipeline_state/<corpus>/)")
    ap.add_argument("--extra", help="text, or a file of text, appended to every job's prompt")
    ap.add_argument("--papers", help="comma-separated paper ids to run (default: all)")
    ap.add_argument("--jobs", help="comma-separated job ids to run, e.g. relate:a+b (default: all selected)")
    ap.add_argument("--rerun", action="store_true", help="run the selected jobs even if the ledger lists them as done")
    ap.add_argument("--plan", action="store_true", help="print what would run, with budget caps, and exit")
    ap.add_argument("--title", help="title of the Synthesis (default: from the number of papers)")
    ap.add_argument("--reset", help="comma-separated job ids whose state on this machine is forgotten (a parked job then "
                    "runs again); runs nothing")
    ap.add_argument("--missing", action="store_true",
                    help="list the papers, code and data not under corpus/, with where to get them, and exit")
    ap.add_argument("--status", action="store_true", help="print the state of every job in this machine's run state and exit")
    a = ap.parse_args(argv)
    if a.corpus:
        try:
            use_corpus(a.corpus)
        except ValueError as e:
            print(e)
            return 2
        if not PAPERS.exists():
            print(f"{PAPERS.relative_to(ROOT)} does not exist: add a paper with python -m pipeline.add --corpus {a.corpus}")
            return 2
    a.state = a.state or STATE
    listed = PAPERS.relative_to(ROOT).as_posix() if PAPERS.is_relative_to(ROOT) else str(PAPERS)
    if a.missing:
        gone = missing_sources(load_papers(PAPERS), ROOT, ROOT / RECORDS)
        for m in gone:
            print(f"{m['id']:20} {m['kind']:9} {m['file']}\n{'':31}{m['title'] or ''}\n{'':31}{m['where'] or 'no DOI or URL in its record'}")
        print(f"{len(gone)} source(s) missing" if gone else "every source in the corpus list is present")
        return 1 if gone else 0
    if a.status:
        db = ROOT / a.state / "state.db"
        if not db.exists():
            print("no pipeline state yet")
            return 0
        now = time.time()
        unpriced = 0
        for r in Orchestrator(db, logs=ROOT / a.state / "logs").status():
            took = (r["finished"] or now) - (r["started"] or now)
            why = f"  {r['error']}" if r["status"] != "passed" and r.get("error") else ""
            u = unreported_usage(ROOT / a.state / "logs", r["id"], transcripts=transcript_dir(ROOT))
            more = f"  + {u['calls']} stopped call(s) not priced: {_tokens(u)}" if u["calls"] else ""
            unpriced += u["calls"]
            print(f"{r['id']:36} {r['status']:8} attempts {r['attempts'] or 0}  ${r['cost_usd'] or 0:6.2f}  "
                  f"turns {r['turns'] or 0:4}  {took / 60:5.1f} min{why}{more}")
        if unpriced:
            print(f"\n{unpriced} call(s) were stopped (a time limit, a crash) before reporting their cost: the dollar "
                  "figures above leave them out, and their tokens are shown instead.")
        return 0
    state = Path(a.state) if Path(a.state).is_absolute() else ROOT / a.state
    if a.reset:
        Orchestrator(state / "state.db", logs=state / "logs").reset(a.reset.split(","))
        print(f"reset: {a.reset} (run again to start {'it' if ',' not in a.reset else 'them'} afresh; add --rerun to "
              "ignore the ledger)")
        return 0
    ps = papers()
    errs = check_papers(ps, ROOT)
    if errs:
        print(f"{listed} has problems:", *errs, sep="\n  ")
        return 2
    ids = [p["id"] for p in ps]
    only = a.papers.split(",") if a.papers else None
    job_ids = a.jobs.split(",") if a.jobs else None
    unknown = sorted(set(only or []) - set(ids))
    if unknown:
        print(f"not in {listed}: {', '.join(unknown)} (add them with python -m pipeline.add)")
        return 2
    stages = a.stages.split(",")
    extra = Path(a.extra).read_text() if a.extra and Path(a.extra).is_file() else (a.extra or "")
    # code and data are related to their papers; papers to what their entries name
    manual = {p["id"]: [*(p.get("relate_with") or []), *(p.get("papers") or [])] for p in ps}
    done = load_completed(LEDGER)
    per = select(jobs(a.model, a.budget_read, a.budget_audit, a.budget_relate, extra=extra,
                      budget_digitize=a.budget_digitize), stages, only, job_ids)

    def ready() -> list[str]:  # records whose per-paper jobs are all done
        return [e["id"] for e in ps if all(f"{s}:{e['id']}" in done for s in stages_of(e))]

    if a.plan:
        print("Per-paper jobs:")
        print("\n".join(plan(per, done, a.rerun)))
        if "relate" in stages:
            pairs, shape_only = split_pairs(candidate_pairs(ROOT / RECORDS, ready(), manual))
            rel = select({"relate": relate_jobs(pairs, a.model, a.budget_relate)}, stages, only, job_ids)
            print("Relation jobs between papers already read:")
            print("\n".join(plan(rel, done, a.rerun)))
            for j in rel:
                print(f"    {j.id}: " + "; ".join(pairs[tuple(_paper_ids(j))]))
            if shape_only:
                print(f"  {len(shape_only)} pair(s) share only a model's shape; listed, not related:")
                for (x, y), why in shape_only.items():
                    print(f"    {x} + {y}: " + "; ".join(why))
            if "validate" in stages:
                val = select({"validate": validate_jobs(pairs, a.model, a.budget_relate)}, stages, only, job_ids)
                print("Validation jobs (each after its pair's relation job; its models against the other's measurements):")
                print("\n".join(plan(val, done, a.rerun)))
            new = [i for i in (only or ids) if i not in ready()]
            if new:
                print(f"  pairs for {', '.join(new)} are found after they are read (budget cap ${a.budget_relate:.0f} each)")
        return 0
    lock = _lock(state)
    if lock is None:
        print(f"another run holds {state / 'run.lock'}; wait for it to finish (one run at a time)")
        return 3
    failed_ingest, reread = [], []
    if "ingest" in stages:
        for p in ps:
            if p.get("kind") in ("software", "dataset") or not _ingest_needed(p):
                continue
            try:
                d = ingest(ROOT / p["file"], p["id"], ROOT / RECORDS, pages=tuple(p["pages"]))
            except Exception as e:  # noqa: BLE001 - one bad PDF stops only its own paper
                failed_ingest.append(p["id"])
                print(f"could not ingest {p['id']}: {e}", flush=True)
                continue
            stale = _stale_rows(done, p["id"])
            if stale:  # its jobs read the old file: they run again on the new one
                forget_completed(LEDGER, stale)
                reread += stale
                done = load_completed(LEDGER)
                print(f"{p['id']}: the PDF or page range changed; {len(stale)} finished job(s) will run again", flush=True)
            print(f"ingested {p['id']} -> {d}", flush=True)
    per = [j for j in per if _paper_ids_of(j.id)[0] not in failed_ingest]
    o = Orchestrator(state / "state.db", agent_bin=a.agent, concurrency=a.concurrency, logs=state / "logs",
                     watch=ROOT, on_passed=_record_passed)
    if reread:  # and on this machine, or its state would still say they passed
        o.reset(sorted(set(reread)))
    results: dict[str, dict] = {}
    todo = pending(per, done, a.rerun)
    if a.rerun:
        o.reset([j.id for j in todo])
    try:
        return _runs(a, o, todo, done, stages, only, job_ids, manual, extra, ps, results, failed_ingest, ids)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\nstopped: its agents were stopped too; run again to resume (finished jobs are kept)", flush=True)
        return 130


def _runs(a, o, todo, done, stages, only, job_ids, manual, extra, ps, results, failed_ingest, ids) -> int:
    def ready() -> list[str]:  # entries whose own jobs are all done, by the ledger as it is now
        return [e["id"] for e in ps if all(f"{s}:{e['id']}" in done for s in stages_of(e))]

    if todo:
        results.update(_run(o, todo, done))
        done = load_completed(LEDGER)
    if "relate" in stages:
        pairs, shape_only = split_pairs(candidate_pairs(ROOT / RECORDS, ready(), manual))
        for (x, y), why in shape_only.items():
            print(f"listed, not related (a shared shape only): {x} + {y}: " + "; ".join(why), flush=True)
        rel = pending(select({"relate": relate_jobs(pairs, a.model, a.budget_relate, extra=extra)}, stages, only, job_ids),
                      done, a.rerun)
        if a.rerun:
            o.reset([j.id for j in rel])
        if rel:
            results.update(_run(o, rel, done))
            done = load_completed(LEDGER)
    if "validate" in stages:  # after a pair's relations are in: its models against the other's measurements
        pairs, _ = split_pairs(candidate_pairs(ROOT / RECORDS, ready(), manual))
        related = {k: v for k, v in pairs.items() if f"relate:{k[0]}+{k[1]}" in done}
        val = pending(select({"validate": validate_jobs(related, a.model, a.budget_relate, extra=extra)}, stages, only, job_ids),
                      done, a.rerun)
        if a.rerun:
            o.reset([j.id for j in val])
        if val:
            results.update(_run(o, val, done))
    needs_person = sorted((jid, r) for jid, r in results.items() if r.get("status") != "passed")
    build_failed = False
    if "build" in stages:
        build_failed = _build(a.title or f"BoxGraph Synthesis: {len(ids)} papers") != 0
    spent = sum(float(r.get("cost_usd") or 0) for r in results.values())
    print(f"\nSummary: {len(results)} job(s) run, ${spent:.2f} spent by them in all.")
    stopped = {jid: unreported_usage(o.logs, jid, transcripts=transcript_dir(ROOT)) for jid in sorted(results)}
    stopped = {jid: u for jid, u in stopped.items() if u["calls"]}
    if stopped:
        print(f"  not in that figure: {sum(u['calls'] for u in stopped.values())} call(s) stopped before reporting "
              f"their cost ({', '.join(stopped)}); their tokens: "
              + _tokens({k: sum(u[k] for u in stopped.values()) for k in USAGE_KEYS}))
    for jid, r in needs_person:
        print(f"  needs a person: {jid} is {r.get('status')}: {r.get('error') or 'see --status'}")
    if failed_ingest:
        print(f"  could not ingest: {', '.join(failed_ingest)}")
    if build_failed:
        print("  the build failed: see its output above")
    if needs_person or failed_ingest or build_failed:
        print(f"  ({a.state}/logs/ has every agent's transcript; `--reset JOB` lets a parked job run again)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
