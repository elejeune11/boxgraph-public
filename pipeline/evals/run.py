"""Run the reader on a synthetic paper and score it against its ground truth.

  python -m pipeline.evals.run [--eval synth_kinetics] [--model MODEL]

The synthetic paper's text is copied into records_eval/<id>/text/ (there is
no PDF, so no page images); the same reader job as for real papers runs on
it; then pipeline.evals.score checks what it found.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import shutil
import sys

import yaml

from pipeline.evals.score import score
from pipeline.orchestrator import Job, Orchestrator
from pipeline.run_papers import PROMPTS, READ_ONLY_SHELL, ROOT, VENV

EVALS = ROOT / "pipeline" / "evals"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eval", default="synth_kinetics")
    ap.add_argument("--model", help="the agent's model (default: its own default)")
    ap.add_argument("--budget", type=float, default=10)
    a = ap.parse_args(argv)
    src = EVALS / a.eval
    gt = yaml.safe_load((src / "ground_truth.yaml").read_text())
    rid = gt["paper"]
    root = ROOT / "records_eval"
    d = root / rid
    if d.exists():
        shutil.rmtree(d)
    if gt.get("pdf"):  # a generated PDF paper: make it, then ingest text and page images
        import subprocess

        from boxgraph.ingest import ingest

        pdf = ROOT / "corpus" / f"eval_{rid}.pdf"
        pdf.parent.mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(src / gt["pdf"]), str(pdf)], check=True)
        ingest(pdf, rid, root)
        n = len(list((d / "text").glob("*.txt")))
        file, note = str(pdf.relative_to(ROOT)), "A generated paper with page images; read its figure as the guide says."
    else:
        (d / "text").mkdir(parents=True)
        for f in (src / "text").glob("page-*.txt"):
            shutil.copy(f, d / "text" / f.name)
        n = len(list((d / "text").glob("*.txt")))
        file, note = f"pipeline/evals/{a.eval} (text only)", "There are no page images for this source; the text is exact."
    prompt = (PROMPTS / "read.md").read_text().format(
        id=rid, file=file, first=1, last=n, page_note=note, others="none",
        date=dt.date.today().isoformat(), model=a.model).replace("records/", "records_eval/")
    tools = ["Read", "Glob", "Grep", f"Write(records_eval/{rid}/**)", f"Edit(records_eval/{rid}/**)",
             f"Bash({VENV}/boxgraph validate:*)", f"Bash({VENV}/boxgraph figure:*)", f"Bash({VENV}/python:*)",
             *READ_ONLY_SHELL]
    job = Job(id=f"eval:{rid}:{dt.datetime.now():%Y%m%d%H%M%S}", kind="eval", prompt=prompt, cwd=str(ROOT),
              validate=[f"{VENV}/boxgraph", "validate", f"records_eval/{rid}"], allowed_tools=tools,
              append_system_prompt_file=str(PROMPTS / "record_guide.md"), model=a.model, max_turns=150,
              budget_usd=a.budget, max_attempts=2)
    state = ROOT / "pipeline_state"
    res = asyncio.run(Orchestrator(state / "evals.db", concurrency=1, logs=state / "logs").run([job]))
    r = res[job.id]
    print(f"reader: {r['status']} after {r['attempts']} attempt(s), ${r['cost_usd'] or 0:.2f}")
    results = score(src, root)
    for name, ok, note in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {note}")
    passed = sum(ok for _, ok, _ in results)
    print(f"{passed}/{len(results)} expectations met")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
