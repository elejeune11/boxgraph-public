"""Panel settings for the second-pass readings (method in _gen.py). For each panel: the printed tick labels
(bottom up, left to right), whether x is logarithmic, and the legend region to leave out (data units: x0,
x1, y0, y1). For each reading: the series colour, the marker shape (the template), whether the marker is
open, the opening radius (px, a little more than half the thinnest drawn line), and the colours drawn over
the series (its markers or bar stems may lie behind them): every other series of the panel, and the panel's
`lines` (a reference line or the threshold line drawn across markers). Bar charts: the bar colour; the group a bar
belongs to (its x value) comes from the order of the bar groups along the axis, matched to the printed
group labels."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("elosegui2016_gen", Path(__file__).with_name("_gen.py"))
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

LOGX = (0.1, 1, 10, 100)
TRAC = (0, 40, 80, 120, 160)
YAP = (1, 2, 3)

FIGS = {
    "fig1a": dict(x=LOGX, y=TRAC, lines=("dark",)),
    "fig1c": dict(x=LOGX, y=(0, 1, 2, 3, 4), lines=("dark",)),
    "fig1e": dict(x=LOGX, y=YAP, lines=("dark",)),
    "fig2a": dict(x=LOGX, y=(0, 0.5, 1.0, 1.5, 2.0, 2.5), legend=[(0.1, 0.5, 1.75, 2.7)]),
    "fig2c": dict(x=LOGX, y=(0, 0.5, 1.0, 1.5, 2.0, 2.5), legend=[(0.1, 0.5, 1.75, 2.7)]),
    "fig3a": dict(x=(0, 10, 20, 30, 40, 50, 60), y=(0, 2, 4, 6, 8), xlog=False, legend=[(25, 62, 6.2, 9.5)],
                  axis_also="blue", lines=("blue",), left_edge=True),
    "fig4a": dict(x=LOGX, y=TRAC, legend=[(0.1, 100, 150, 230)]),
    "fig4b": dict(x=LOGX, y=YAP),
    "fig4c": dict(x=(0, 5, 10, 15), y=(0, 1, 2), xlog=False),
    "fig4e": dict(x=None, y=TRAC, groups=("5", "29")),
    "fig4f": dict(x=None, y=(0, 1, 2, 3), groups=("5", "29")),
    "fig5a": dict(x=LOGX, y=TRAC, legend=[(0.1, 0.6, 165, 260)]),
    "fig5b": dict(x=LOGX, y=YAP),
    "fig5c": dict(x=(0, 5, 10, 15, 20), y=(0, 1, 2, 3), xlog=False),
    "fig5e": dict(x=LOGX, y=TRAC),
    "fig5f": dict(x=LOGX, y=YAP, ydrop=1),
    "fig6j": dict(x=LOGX, y=YAP, legend=[(0.1, 0.5, 2.2, 3.6)]),
    "fig6k": dict(x=LOGX, y=YAP, legend=[(0.1, 0.5, 2.2, 3.6)], lines=("blue",)),
    "fig6l": dict(x=LOGX, y=YAP, legend=[(0.1, 0.5, 2.2, 3.6)], lines=("blue",)),
    "figs1b": dict(x=None, y=(0, 20, 40, 60, 80, 100), groups=("control", "shrna")),
    "figs2": dict(x=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), y=(0, 100, 200, 300), xlog=False, tick=22),
    "figs3a": dict(x=LOGX, y=(0, 1, 2, 3, 4)),
    "figs3b": dict(x=LOGX, y=(0, 5, 10, 15, 20, 25), tick=16),
    "figs4a": dict(x=LOGX, y=(0, 200, 400, 600, 800, 1000, 1200), legend=[(0.1, 0.4, 1050, 1400)]),
    "figs4c": dict(x=LOGX, y=(0.0, 0.4, 0.8, 1.2, 1.6), legend=[(0.1, 0.4, 1.45, 1.9)]),
    "figs4e": dict(x=LOGX, y=(0.0, 0.4, 0.8, 1.2, 1.6)),
    "figs5a": dict(x=LOGX, y=(0, 20, 40, 60, 80, 100, 120, 140, 160, 180), legend=[(0.1, 0.5, 182, 260)]),
    "figs5b": dict(x=LOGX, y=(0, 1, 2, 3)),
    "figs5c": dict(x=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), y=(0, 1, 2, 3, 4, 5, 6), xlog=False),
    "figs6": dict(x=(0, 20, 40, 60, 80, 100), y=(0, 200, 400, 600, 800, 1000, 1200), xlog=False,
                  legend=[(2.5, 14, 1020, 1300)]),
}

# Supplementary Fig. 2: the scatter of single transfected cells lies over 0-1 of the x axis; the means of
# untransfected control cells (left) and talin 2 shRNA cells (right) lie outside it
S2_SCATTER = [(-1.0, -0.04, -100, 400), (1.04, 3.0, -100, 400)]
S2_LEFT = [(-0.04, 3.0, -100, 400)]
S2_RIGHT = [(-1.0, 1.04, -100, 400)]
S2_LEGEND = [(-0.45, -0.25, 230, 320)]

# reading id -> (figure, colour, marker shape, hollow, open_r, covering colours, extra)
SERIES = {
    "fig1a_control": ("fig1a", "red", "tri_up", False, 6, ("blue", "black"), {"part": 0.1}),
    "fig1a_shrna": ("fig1a", "blue", "tri_down", False, 6, ("black",), {}),
    "fig1a_l325r": ("fig1a", "black", "diamond", True, 6, (), {}),
    "fig1a_bg": ("fig1a", "grey", "disc", False, 6, ("red", "blue", "black"), {"cap_max": 160}),
    "fig1c_control": ("fig1c", "red", "tri_up", False, 6, ("blue", "black"), {"part": 0.1}),
    "fig1c_shrna": ("fig1c", "blue", "tri_down", False, 6, ("black",), {"part": 0.12}),
    "fig1c_l325r": ("fig1c", "black", "diamond", True, 6, (), {}),
    "fig1e_control": ("fig1e", "red", "tri_up", False, 6, ("blue", "black"), {"part": 0.1}),
    "fig1e_shrna": ("fig1e", "blue", "tri_down", False, 6, ("black",), {"part": 0.12}),
    "fig1e_l325r": ("fig1e", "black", "diamond", True, 6, (), {}),
    "fig2a_control": ("fig2a", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "fig2a_shrna": ("fig2a", "blue", "disc", False, 6, (), {}),
    "fig2c_control": ("fig2c", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "fig2c_shrna": ("fig2c", "blue", "disc", False, 6, (), {}),
    "fig3a_lifetime": ("fig3a", "red", "disc", False, 5, (), {"cap_max": 200}),
    "fig4a_fl": ("fig4a", "red", "disc", False, 6, ("blue", "black"), {"part": 0.2}),
    "fig4a_rod": ("fig4a", "blue", "disc", False, 6, ("black",), {"part": 0.2}),
    "fig4a_head": ("fig4a", "black", "disc", False, 6, (), {}),
    "fig4b_fl": ("fig4b", "red", "disc", False, 6, ("blue", "black"), {"part": 0.2}),
    "fig4b_rod": ("fig4b", "blue", "disc", False, 6, ("black",), {"part": 0.2}),
    "fig4b_head": ("fig4b", "black", "disc", False, 6, (), {}),
    "fig4c_fl": ("fig4c", "red", "disc", False, 9, ("blue", "black"), {"part": 0.2, "stem": 7}),
    "fig4c_rod": ("fig4c", "blue", "disc", False, 9, ("black",), {"part": 0.2, "stem": 7}),
    "fig4c_head": ("fig4c", "black", "disc", False, 9, (), {"stem": 7}),
    "fig5a_fl": ("fig5a", "red", "disc", False, 6, ("blue", "grey"), {"part": 0.2}),
    "fig5a_ivvi": ("fig5a", "blue", "disc", False, 6, ("grey",), {"part": 0.2}),
    "fig5a_shrna": ("fig5a", "grey", "disc", False, 6, (), {}),
    "fig5b_fl": ("fig5b", "red", "disc", False, 6, ("blue", "grey"), {"part": 0.2}),
    "fig5b_ivvi": ("fig5b", "blue", "disc", False, 6, ("grey",), {"part": 0.2}),
    "fig5b_shrna": ("fig5b", "grey", "disc", False, 6, (), {}),
    "fig5c_fl": ("fig5c", "red", "disc", False, 10, ("blue", "grey"), {"part": 0.2, "stem": 8}),
    "fig5c_ivvi": ("fig5c", "blue", "disc", False, 10, ("grey",), {"part": 0.2, "stem": 8}),
    "fig5c_shrna": ("fig5c", "grey", "disc", False, 10, (), {"stem": 8}),
    "fig5e_vd1": ("fig5e", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "fig5e_a50i": ("fig5e", "blue", "disc", False, 6, (), {}),
    "fig5f_vd1": ("fig5f", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "fig5f_a50i": ("fig5f", "blue", "disc", False, 6, (), {}),
    "fig6j_fn1": ("fig6j", "red", "disc", False, 10, ("blue", "black"), {"part": 0.2, "stem": 8}),
    "fig6j_fn10": ("fig6j", "blue", "disc", False, 10, ("black",), {"part": 0.2, "stem": 8}),
    "fig6j_fn100": ("fig6j", "black", "disc", False, 10, (), {"stem": 8}),
    "fig6k_gpen005": ("fig6k", "red", "disc", False, 10, ("green", "black"), {"part": 0.2, "stem": 8}),
    "fig6k_gpen015": ("fig6k", "green", "disc", False, 10, ("black",), {"part": 0.2, "stem": 8}),
    "fig6k_gpen050": ("fig6k", "black", "disc", False, 10, (), {"stem": 8}),
    "fig6l_bleb5": ("fig6l", "red", "disc", False, 10, ("green", "black"), {"part": 0.2, "stem": 8}),
    "fig6l_bleb15": ("fig6l", "green", "disc", False, 10, ("black",), {"part": 0.2, "stem": 8}),
    "fig6l_bleb50": ("fig6l", "black", "disc", False, 10, (), {"stem": 8}),
    "figs2_l325r_5kpa": ("figs2", "blue", "disc", False, 4, ("red",),
                         {"part": 0.3, "exclude": S2_SCATTER, "one_per_x": False, "bars": False}),
    "figs2_l325r_29kpa": ("figs2", "red", "disc", False, 4, ("blue",),
                          {"part": 0.3, "exclude": S2_SCATTER, "one_per_x": False, "bars": False}),
    "figs3a_control": ("figs3a", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "figs3a_shrna": ("figs3a", "blue", "disc", False, 6, (), {}),
    "figs3b_control": ("figs3b", "red", "disc", False, 10, ("blue",), {"part": 0.2, "stem": 9}),
    "figs3b_shrna": ("figs3b", "blue", "disc", False, 10, (), {"stem": 9}),
    "figs4a_control": ("figs4a", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "figs4a_shrna": ("figs4a", "blue", "disc", False, 6, (), {}),
    "figs4c_control": ("figs4c", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "figs4c_shrna": ("figs4c", "blue", "disc", False, 6, (), {}),
    "figs4e_wt": ("figs4e", "black", "disc", False, 6, (), {}),
    "figs5a_vd1": ("figs5a", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "figs5a_a50i": ("figs5a", "blue", "disc", False, 6, (), {}),
    "figs5b_vd1": ("figs5b", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
    "figs5b_a50i": ("figs5b", "blue", "disc", False, 6, (), {}),
    "figs5c_vd1": ("figs5c", "red", "disc", False, 6, ("blue",), {"part": 0.3, "one_per_x": False, "bars": False}),
    "figs5c_a50i": ("figs5c", "blue", "disc", False, 6, ("red",), {"part": 0.3, "one_per_x": False, "bars": False}),
    "figs6_5kpa": ("figs6", "blue", "disc", False, 6, ("red",), {"part": 0.2}),
    "figs6_29kpa": ("figs6", "red", "disc", False, 6, ("blue",), {"part": 0.2}),
}

# Supplementary Fig. 2 means: (colour, exclude, x value: the rigidity of that colour, as the legend says)
S2_MEANS = {
    "figs2_control_5kpa": ("blue", S2_LEFT), "figs2_control_29kpa": ("red", S2_LEFT),
    "figs2_shrna_5kpa": ("blue", S2_RIGHT), "figs2_shrna_29kpa": ("red", S2_RIGHT),
}

# bar readings: id -> (figure, bar colour, position within its group (0-based, from the left) or None)
BARS = {
    "fig4e_shrna": ("fig4e", "grey"), "fig4e_fl": ("fig4e", "red"), "fig4e_l325r": ("fig4e", "blue"),
    "fig4e_w359a": ("fig4e", "black"),
    "fig4f_shrna": ("fig4f", "grey"), "fig4f_fl": ("fig4f", "red"), "fig4f_l325r": ("fig4f", "blue"),
    "fig4f_w359a": ("fig4f", "black"),
}
for _cell in ("control", "shrna"):
    for _t, _c in (("none", "black"), ("ab", "lightblue"), ("gpen", "pink"), ("both", "red")):
        BARS[f"figs1b_{_cell}_{_t}"] = ("figs1b", _c, _cell)


def _cover(img, colours):
    cov = None
    for c in colours:
        mc = gen.mask_of(img, c)
        cov = mc if cov is None else (cov | mc)
    return cov


def _bar_cal(img, f):
    """A bar chart has no x scale: the y axis is calibrated, the x map is the identity (columns)."""
    return gen.calibrate(img, None, f["y"])


def read(image, at, rid):
    img = np.asarray(image)
    if rid in BARS:
        return read_bars(img, rid)
    if rid in S2_MEANS:
        colour, excl = S2_MEANS[rid]
        f = FIGS["figs2"]
        cal = gen.calibrate(img, f["x"], f["y"], xlog=False, tick=f["tick"])
        cal.right = img.shape[1] - 1   # the shRNA means stand right of the x axis's end
        # the means are drawn with the scatter's marker: its size is measured on the scatter
        from scipy import ndimage
        inside = gen.box_mask(img.shape[:2], cal, S2_SCATTER)
        size = gen.marker_size([ndimage.binary_opening(gen.mask_of(img, c) & inside, structure=gen._disc(4))
                                for c in ("red", "blue")], "disc")
        out = gen.read_series(img, cal, colour, 4, "disc", exclude=excl + S2_LEGEND, size=size,
                              x_of=lambda c: 5.0 if colour == "blue" else 29.0)
        for r in out:
            r["note"] += "; x is the rigidity the legend gives this colour (5 kPa blue, 29 kPa red)"
        return out
    if rid == "fig3a_unfolding":   # the blue line: talin unfolding times of ref. 25
        f = FIGS["fig3a"]
        cal = gen.calibrate(img, f["x"], f["y"], xlog=False, axis_also="blue")
        return gen.read_line_at(img, cal, "blue", [float(a) for a in at], exclude=f["legend"])
    fig, colour, shape, hollow, open_r, cover, extra = SERIES[rid]
    f = FIGS[fig]
    extra = dict(extra)
    exclude = list(f.get("legend", ())) + list(extra.pop("exclude", ()))
    cal = gen.calibrate(img, f["x"], f["y"], xlog=f.get("xlog", True), ydrop=f.get("ydrop", 0),
                        tick=f.get("tick", 36), axis_also=f.get("axis_also"))
    if f.get("left_edge"):   # markers at x = 0 stand on the y axis: the box reaches left of it
        cal.left = 0
    mates = [v for v in SERIES.values() if v[0] == fig]
    if "size" not in extra and len(mates) > 1 and all(v[2] == "disc" and not v[3] for v in mates):
        # one disc marker for every series of the panel: its size is measured on all of them together
        inside = gen.box_mask(img.shape[:2], cal, exclude)
        from scipy import ndimage
        fl = [ndimage.binary_opening(gen.mask_of(img, v[1]) & inside, structure=gen._disc(v[4])) for v in mates]
        extra["size"] = gen.marker_size(fl, "disc")
    # any other series of the panel may be drawn over this one
    cover = sorted(set(cover) | {v[1] for v in mates if v[1] != colour} | set(f.get("lines", ())))
    extra.setdefault("part", 0.2)
    return gen.read_series(img, cal, colour, open_r, shape, hollow=hollow, exclude=exclude,
                           cover=_cover(img, cover) if cover else None, **extra)


def read_bars(img, rid):
    fig, colour = BARS[rid][:2]
    only = BARS[rid][2] if len(BARS[rid]) > 2 else None
    f = FIGS[fig]
    cal = gen.calibrate(img, None, f["y"])
    # all bars of the panel (every colour), to find the groups: split at the widest gap between bars
    allb = []
    for c in sorted({v[1] for v in BARS.values() if v[0] == fig}):
        allb += [(b["col"], c) for b in gen.read_bar_tops(img, cal, c)]
    allb.sort()
    cols = [c for c, _ in allb]
    gaps = np.diff(cols)
    cut = cols[int(np.argmax(gaps))] + gaps.max() / 2
    mine = gen.read_bar_tops(img, cal, colour)
    out = []
    for b in mine:
        g = f["groups"][0] if b["col"] < cut else f["groups"][1]
        if only is not None and g != only:
            continue
        rec = {k: v for k, v in b.items() if k != "col"}
        # Fig. 4e,f: the groups are the printed rigidities; Supplementary Fig. 1b: all on 29 kPa gels
        rec["x"] = float(g) if g.isdigit() else 29.0
        rec["note"] += f"; group '{g}' (bars split at the widest gap between the {len(cols)} bars)"
        out.append(rec)
    return out
