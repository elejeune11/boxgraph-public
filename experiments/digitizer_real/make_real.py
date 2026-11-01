"""Real figure panels with known answers, for the digitizer comparison.

A panel qualifies when the paper says which equation it plots and the build computes that
equation at the read positions. The equation's value is taken as the truth. The panel is cut out
of the page so the equations printed around it are not visible, and saved as a one-page PDF.

  python -m experiments.digitizer_real.make_real --out experiments_work/digitizer_real/figures
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import tempfile
from pathlib import Path

import yaml
from PIL import Image

from boxgraph import precision as P

ROOT = Path(__file__).resolve().parents[2]
DPI = 600
MARGIN = 40  # pixels at 300 dpi around the recorded crop, so tick labels are kept

# panels whose y axis is labelled "log N" / "log T" with plain numbers
LOG_LABELLED = {"fig3a_N2", "fig3a_N10", "fig3d_stoch_N10", "fig4b_g1"}
LOG_X = {"fig4a_N100"}  # x axis printed as "log f/N0"

# (record, figure reading id, comparison whose computed side is the plotted equation)
PANELS = [
    ("bell1978", "fig8_KL300", "cmp_fig8_KL300_eq17"),
    ("bell1978", "fig8_KL1e4", "cmp_fig8_KL1e4_eq17"),
    ("erdmann2004", "fig2b_p5", "cmp_fig2b_p5"),
    ("erdmann2004", "fig3a_N2", "cmp_fig3a_N2"),
    ("erdmann2004", "fig3a_N10", "cmp_fig3a_N10"),
    ("erdmann2004", "fig3d_stoch_N10", "cmp_fig3d_stoch_N10"),
    ("erdmann2004", "fig4a_N100", "cmp_fig4a_N100"),
    ("erdmann2004", "fig4b_g1", "cmp_fig4b_g1"),
]


def _label(s) -> float:
    return P.parse(str(s)).value


def make(out: Path, synthesis: Path = ROOT / "build" / "synthesis.json") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    syn = json.loads(synthesis.read_text())
    truth = {}
    for sid, fid, cmp in PANELS:
        fr = {f["id"]: f for f in yaml.safe_load((ROOT / "records" / sid / "figures.yaml").read_text())}[fid]
        src = ROOT / yaml.safe_load((ROOT / "records" / sid / "source.yaml").read_text())["file"]
        v = {x["comparison"]: x for x in syn["papers"][sid]["verdicts"]}[cmp]
        at = [_label(a) for a in fr["at"]]
        assert len(v["computed_value"]) == len(at), (fid, cmp)
        x0, y0, x1, y1 = fr["crop"]
        k = DPI / fr.get("dpi", 300)
        box = [max(0, x0 - MARGIN), max(0, y0 - MARGIN), x1 + MARGIN, y1 + MARGIN]
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(fr["page"]), "-l", str(fr["page"]), "-png",
                            "-singlefile", "-x", str(int(box[0] * k)), "-y", str(int(box[1] * k)),
                            "-W", str(int((box[2] - box[0]) * k)), "-H", str(int((box[3] - box[1]) * k)),
                            str(src), f"{td}/p"], check=True)
            Image.open(f"{td}/p.png").convert("RGB").save(out / f"{fid}.pdf", resolution=DPI)
        marks = [_label(m[1]) for m in fr["y"]["marks"]]
        ys, scale, span = v["computed_value"], fr["y"]["scale"], [min(marks), max(marks)]
        if fid in LOG_LABELLED:  # the axis is printed as log10 of the quantity: answers come in those units
            ys, scale, span = [math.log10(y) for y in ys], "linear", [math.log10(m) for m in span]
        if fid in LOG_X:
            at = [math.log10(a) for a in at]
        truth[fid] = {"what": fr["what"] + f" (panel {fr['where']})", "at": at, "y": ys,
                      "scale": scale, "span": span, "record": sid, "comparison": cmp}
    (out / "truth.json").write_text(json.dumps(truth, indent=1))
    return truth


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "experiments_work" / "digitizer_real" / "figures"))
    make(Path(ap.parse_args().out))
