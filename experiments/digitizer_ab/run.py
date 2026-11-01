"""Compare three ways of digitizing figures on figures with known answers.

  python -m experiments.digitizer_ab.run [--reps 2] [--concurrency 6]

Arms:
  hybrid  the agent uses the BoxGraph figure tools and writes a spec; code reads it
  eye     the agent reads values by looking at rendered images; no code
  code    the agent writes its own Python; it may not read or use the BoxGraph digitizer
Every arm gets the same figure, the same request and the same answer format.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import shutil
import sqlite3
import sys
from pathlib import Path

from experiments.digitizer_ab.make_figures import make
from experiments.digitizer_ab.score import consistency, score_run
from pipeline.orchestrator import Job, Orchestrator

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VENV = ROOT / ".venv" / "bin"
ARMS = ("hybrid", "eye", "code")

ASK = """Page 1 of `fig.pdf` in your working directory holds one figure and its caption.

Read {what} at x = {at}.

For each x, give your best value of y on the plotted curve or point, and an interval [lo, hi] that you
are 95% confident contains it. Be honest about the interval: too narrow is as wrong as too wide.
Give x and y in the units the axis labels are printed in (on an axis labelled "log N", give log N).

You are already in your working directory. Run one simple command per Bash call: no `cd`, `;`, `&&`,
pipes or variable assignments, which are refused.
"""

ANSWER = """Write the result to `answer.json` in your working directory:
{{"readings": [{{"x": <x>, "y": <value>, "lo": <low>, "hi": <high>}}, ...], "notes": "<how you read it>"}}
"""

ARM_TEXT = {
    "eye": """Work by looking only. Render the page or parts of it as images with pdftoppm and open them with
the Read tool; for example `pdftoppm -r 300 -png -singlefile fig.pdf page` renders the page, and
`pdftoppm -r 600 -x X -y Y -W W -H H -png -singlefile fig.pdf zoom` renders a zoomed region. Do not
write or run any code. """ + ANSWER,
    "code": """You may write and run Python ({py}; numpy, scipy, Pillow and matplotlib are installed) and
pdftoppm to measure the figure however you like. Do not read, import or call the `boxgraph` package or
its tools; write your own method. """ + ANSWER,
    "hybrid": """Use the BoxGraph figure tools, as the guide's section "Reading figures" explains:
  {bg} figure page fig.pdf 1 --out page.png
  {bg} figure axes fig.pdf 1 --crop X0,Y0,X1,Y1 --out axes.png
Then write `spec.yaml`: one figure reading in the guide's format, plus a line `pdf: fig.pdf`. Use
`id: fig`, `page: 1`, `at:` the x positions above (for points, use mode: markers and no `at`).
Check it with
  {bg} figure read spec.yaml --out answer.json --overlay check.png
and open check.png. The answer is whatever `figure read` writes: do not write answer.json yourself.
""",
}

CHECK = """import json, sys
a = json.load(open("answer.json"))
xs = {xs}
got = [r for r in a.get("readings", []) if r.get("y") is not None]
missing = [x for x in xs if not any(abs(float(r["x"]) - x) <= 0.05 * (1 + abs(x)) for r in got)]
if missing:
    print("ERROR: no value for x =", missing); sys.exit(1)
print("ok")
"""


def jobs(work: Path, truth: dict, reps: int, model: str) -> list[Job]:
    out = []
    for fig, t in truth.items():
        for arm in ARMS:
            for rep in range(1, reps + 1):
                d = work / arm / fig / f"r{rep}"
                d.mkdir(parents=True, exist_ok=True)
                shutil.copy(work / "figures" / f"{fig}.pdf", d / "fig.pdf")
                (d / "check.py").write_text(CHECK.format(xs=t["at"]))
                at = ", ".join(f"{x:g}" for x in t["at"])
                prompt = ASK.format(what=t["what"], at=at) + "\n" + ARM_TEXT[arm].format(py=VENV / "python",
                                                                                             bg=VENV / "boxgraph")
                writes = [f"Write(//{d.as_posix().lstrip('/')}/**)", f"Edit(//{d.as_posix().lstrip('/')}/**)",
                          "Write(*)", "Edit(*)"]
                tools = ["Read", "Glob", "Bash(pdftoppm:*)", "Bash(ls:*)", "Bash(mkdir:*)", *writes]
                deny = []
                if arm == "eye":
                    validate = [str(VENV / "python"), "check.py"]
                elif arm == "code":
                    tools += [f"Bash({VENV / 'python'}:*)", f"Bash({VENV / 'python'} :*)"]
                    deny = [f"Read(//{(ROOT / 'boxgraph').as_posix().lstrip('/')}/**)", f"Bash({VENV / 'boxgraph'}:*)"]
                    validate = [str(VENV / "python"), "check.py"]
                else:
                    tools += [f"Bash({VENV / 'boxgraph'} figure:*)"]
                    validate = ["sh", "-c", f"{VENV / 'boxgraph'} figure read spec.yaml --out answer.json >/dev/null; "
                                f"{VENV / 'python'} check.py"]
                out.append(Job(
                    id=f"{arm}:{fig}:r{rep}", kind=arm, prompt=prompt, cwd=str(d), validate=validate,
                    allowed_tools=tools, disallowed_tools=deny, model=model, max_turns=80, budget_usd=4.0,
                    max_attempts=2, timeout_s=3600,
                    append_system_prompt_file=str(ROOT / "pipeline" / "prompts" / "record_guide.md") if arm == "hybrid" else None))
    return out


def report(work: Path, truth: dict, reps: int, arms: tuple[str, ...] = ARMS) -> str:
    db = sqlite3.connect(work / "state.db")
    rows = {r[0]: r for r in db.execute("select id, status, cost_usd, started, finished from jobs")}
    per: dict = {}
    for fig, t in truth.items():
        for arm in arms:
            answers = []
            for rep in range(1, reps + 1):
                f = work / arm / fig / f"r{rep}" / "answer.json"
                try:
                    answers.append(json.loads(f.read_text()))
                except (OSError, json.JSONDecodeError):
                    answers.append({})
            scores = [score_run(a, t) for a in answers]
            cons = consistency(answers[0], answers[1], t) if reps > 1 else math.nan
            jid = [f"{arm}:{fig}:r{r}" for r in range(1, reps + 1)]
            cost = sum((rows.get(j, (0, 0, 0))[2] or 0) for j in jid)
            mins = sum(((rows[j][4] or 0) - (rows[j][3] or 0)) / 60 for j in jid if j in rows and rows[j][4])
            per[(fig, arm)] = {"scores": scores, "consistency": cons, "cost": cost, "minutes": mins,
                               "status": [rows.get(j, (0, "missing"))[1] for j in jid]}
    lines = ["# Digitizer comparison: results", "",
             "Errors are a fraction of the axis span (in decades on the log axis), averaged over the read positions.",
             "Coverage is the share of true values inside the claimed 95% interval. Width is the mean interval width,",
             "as a fraction of the axis. Spread is the mean difference between the two runs of the same method.", "",
             "| Figure | Method | Mean error | Max error | Coverage | Width | Missing | Spread | Cost | Status |",
             "|---|---|---|---|---|---|---|---|---|---|"]

    def f(x, pct=True):
        return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{100 * x:.2f}%" if pct else f"{x:.2f}")

    totals = {a: {"err": [], "cov": [], "width": [], "missing": 0, "spread": [], "cost": 0.0} for a in arms}
    for fig in truth:
        for arm in arms:
            p = per[(fig, arm)]
            sc = p["scores"]
            me = [s["mean_err"] for s in sc if not math.isnan(s["mean_err"])]
            mx = [s["max_err"] for s in sc if not math.isnan(s["max_err"])]
            wd = [s["mean_width"] for s in sc if not math.isnan(s["mean_width"]) and not math.isinf(s["mean_width"])]
            cov = sum(s["coverage"] for s in sc) / len(sc)
            miss = sum(s["missing"] for s in sc)
            lines.append(f"| {fig} | {arm} | {f(sum(me) / len(me) if me else math.nan)} | {f(max(mx) if mx else math.nan)} | "
                         f"{cov:.0%} | {f(sum(wd) / len(wd) if wd else math.nan)} | {miss} | {f(p['consistency'])} | "
                         f"${p['cost']:.2f} | {', '.join(p['status'])} |")
            t = totals[arm]
            t["err"] += me
            t["cov"].append(cov)
            t["width"] += wd
            t["missing"] += miss
            if not math.isnan(p["consistency"]):
                t["spread"].append(p["consistency"])
            t["cost"] += p["cost"]
    lines += ["", "## Totals", "", "| Method | Mean error | Coverage | Width | Missing | Spread | Cost |", "|---|---|---|---|---|---|---|"]
    for arm in arms:
        t = totals[arm]
        avg = lambda xs: sum(xs) / len(xs) if xs else math.nan  # noqa: E731
        lines.append(f"| {arm} | {f(avg(t['err']))} | {avg(t['cov']):.0%} | {f(avg(t['width']))} | {t['missing']} | "
                     f"{f(avg(t['spread']))} | ${t['cost']:.2f} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--model", help="the agent's model (default: its own default)")
    ap.add_argument("--work", default=str(ROOT / "experiments_work" / "digitizer_ab"))
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--results", default=str(HERE / "RESULTS.md"), help="where to write the results table")
    ap.add_argument("--figs", help="comma-separated subset of figures, for a pilot")
    ap.add_argument("--arms", help="comma-separated subset of methods to (re)run")
    a = ap.parse_args(argv)
    work = Path(a.work)
    truth = make(work / "figures") if not (work / "figures" / "truth.json").exists() else \
        json.loads((work / "figures" / "truth.json").read_text())
    if a.figs:
        truth = {k: v for k, v in truth.items() if k in a.figs.split(",")}
    if not a.report_only:
        js = jobs(work, truth, a.reps, a.model)
        if a.arms:
            js = [j for j in js if j.kind in a.arms.split(",")]
        asyncio.run(Orchestrator(work / "state.db", concurrency=a.concurrency, logs=work / "logs").run(js))
    arms = tuple(x for x in ARMS if not a.arms or x in a.arms.split(","))
    text = report(work, truth, a.reps, arms)
    Path(a.results).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
