"""Shared code for Figs. 4b and 4c (p. 8): two groups, x = 1 control, x = 2 IL-1beta.

Fig. 4b: a grey violin per group with a thick black dashed line (taken as the median: GraphPad violins draw
the median dashed and the quartiles dotted) and two thinner dotted lines (the quartiles), plus three large
black dots per group (one per network). Fig. 4c: a light grey beeswarm per group with a black dashed central
line and three large black dots. A significance bar ('ns', '***') lies above the data: rows above `ymax` are
not searched for lines.

The dashed line is the line group of highest cover with pixels darker than 90 (_cols.central_line). The
quartiles are the nearest line groups above and below it when pixels darker than 150 are counted (the dotted
lines are thinner and lighter), excluding the dashed line's own rows.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_cols", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cols.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

PANELS = {
    "4b": dict(box=(2500, 4000, 100, 3000), labels=[100, 80, 60, 40, 20, 0], log=False, ymax=90.0, wfrac=0.15),
    "4c": dict(box=(450, 1950, 100, 3100), labels=[4, 3, 2, 1, 0], log=True, ymax=3000.0, wfrac=0.3),
}


def cal_of(image, panel):
    p = PANELS[panel]
    return C.calibrate(image, p["box"], p["labels"], p["log"]), p


def read_median(image, at, panel):
    cal, p = cal_of(image, panel)
    return C.read_column(image, at, cal, wfrac=p["wfrac"], ymax=p["ymax"], what="dashed central line")


def read_quartile(image, at, panel, which):
    cal, p = cal_of(image, panel)
    out = []
    for x in at:
        k = int(round(x))
        med = C.central_line(cal, k, wfrac=p["wfrac"], ymax=p["ymax"])
        groups = [g for g in C.line_groups(cal, k, wfrac=p["wfrac"], cover=0.3, black=150, ymax=p["ymax"])
                  if abs(g[0] - med[0]) > med[1] + 4]
        side = [g for g in groups if (g[0] < med[0] if which == "upper" else g[0] > med[0])]
        if not side:
            out.append({"x": x, "y": None, "note": f"group {k}: no dotted {which} quartile line found"})
            continue
        r, tol, fr = min(side, key=lambda g: abs(g[0] - med[0]))
        lo, hi = sorted((C.val(cal, r + tol), C.val(cal, r - tol)))
        out.append({"x": x, "y": C.val(cal, r), "lo": lo, "hi": hi, "px": [float(cal["cols"][k - 1]), r],
                    "note": f"group {k}: dotted {which} quartile line at row {r:.1f} (cover {fr:.2f}); "
                            f"misfit {cal['mis']:.2f} px"})
    return out


def read_network_dots(image, panel):
    cal, p = cal_of(image, panel)
    return C.read_dots(image, cal, [1, 2], dot_core=25, ymax=p["ymax"])
