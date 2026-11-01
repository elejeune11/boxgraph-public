"""Score a reading of a synthetic paper against its ground truth.

  python -m pipeline.evals.score pipeline/evals/synth_kinetics records_eval

Builds the Synthesis over the eval records and checks each expectation:
a finding of a kind on a page, a reproduced verdict on a page, an open
question of a kind on a page, and that no printed value was corrected.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from boxgraph.synthesis import build_synthesis


def score(eval_dir: Path, records: Path) -> list[tuple[str, bool, str]]:
    gt = yaml.safe_load((eval_dir / "ground_truth.yaml").read_text())
    pid = gt["paper"]
    syn = build_synthesis(records)
    paper = syn["papers"].get(pid)
    results = []
    if not paper or not paper.get("sound"):
        return [("record is sound", False, str(paper and paper.get("errors")))]
    results.append(("record is sound", True, ""))
    data = paper["data"]
    findings = [f for f in syn["findings"] if f["source"] == pid]
    figure_data = {k for k, d in data.items() if str(d.get("printed", "")).startswith("read from figure")}
    for e in gt["expect"]:
        if e.get("figure_datum"):
            results.append((e["id"], bool(figure_data), f"figure data: {sorted(figure_data)}"))
            continue
        if "figure_finding" in e:
            hit = [f for f in findings if f["kind"] == e["figure_finding"]
                   and f["subject"].split("/", 1)[-1] in figure_data]
            results.append((e["id"], bool(hit), f"{len(hit)} finding(s) of kind {e['figure_finding']} on figure data"))
            continue
        if "finding" in e:
            def page_of(f):
                if f.get("page"):
                    return f["page"]
                for t in [f["subject"], *f.get("trace", [])]:
                    loc = t.split("/", 1)[-1]
                    if loc in data:
                        return data[loc]["page"]
                return None
            hit = [f for f in findings if f["kind"] == e["finding"]]
            ok = any(page_of(f) in (e["page"], None) for f in hit)
            results.append((e["id"], ok, f"{len(hit)} finding(s) of kind {e['finding']}"))
        elif "verdict_reproduced_on_page" in e:
            ok = any(v["verdict"] == "reproduced" and v["page"] == e["verdict_reproduced_on_page"] for v in paper["verdicts"])
            results.append((e["id"], ok, ""))
        elif "question_kind" in e:
            ok = any(q["kind"] == e["question_kind"] for q in paper["questions"])
            added = paper.get("added") or {}
            results.append((e["id"], ok or bool(added), f"questions {[q['kind'] for q in paper['questions']]}, added {list(added)}"))
    forbidden = {"synth_kinetics": ("9.5x10^-2", "0.095"), "synth_figure": ("0.7",)}.get(pid, ())
    corrected = any(str(d.get("printed")).replace(" ", "") in forbidden for d in data.values())
    corrected |= any(str(a.get("printed")).replace(" ", "") in forbidden for a in (paper.get("added") or {}).values())
    results.append(("printed values not corrected", not corrected, ""))
    return results


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    res = score(Path(argv[0]), Path(argv[1]))
    for name, ok, note in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {note}")
    passed = sum(ok for _, ok, _ in res)
    print(f"{passed}/{len(res)} expectations met")
    return 0 if passed == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
