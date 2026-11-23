"""Shared code for the speed histograms of Owen et al. 2017 (Fig. 3B, 3C, 4A, 5B, S14C, S14E):
MATLAB histograms with transparent, outlined faces in a light-grey box. Loaded with hash pinning by
the reading files, which give a CONFIG.

Calibration (all positions from the image; only the printed labels are typed in, in CONFIG):
- frame: pixels of low saturation (max-min channel < 30) and grey level 60-215 (the light-grey
  box, its tick stubs). The box lines are the frame rows / columns covering > 40% of the crop
  (`_kit.box_lines`); if the frame is hidden under the faces, CONFIG gives which lines exist.
- x: CONFIG["x_spines"] gives the values at the left and right box lines (e.g. 0 and 150 when the
  labels sit under the spines), and CONFIG["x_ticks"] the labels of tick stubs found on the top
  or bottom box line (CONFIG["x_tick_line"]), matched in order.
- y: tick stubs on the left or right box line (CONFIG["y_tick_spine"]) matched in order (bottom
  to top) to CONFIG["y_ticks"] (where bar outlines touch the spine and give extra candidates, the
  evenly spaced subset is kept, as for x); with CONFIG["y_base_zero"] the bars' baseline is also a mark at 0.
- faces: colour masks (tolerance CONFIG["tol"]) of each series' face colour and of the overlap
  colour; outline: dark pixels (grey < 90). Bars are read by `_kit.histogram`.
"""
import numpy as np


def frame_mask(k, image):
    img = k.rgb(image)
    sat = img.max(axis=2) - img.min(axis=2)
    g = img.mean(axis=2)
    return (sat < 30) & (g > 60) & (g < 215)


def read(k, image, C):
    img = k.rgb(image)
    fr = frame_mask(k, image) | k.dark_mask(image, 90)
    vc, hr = k.box_lines(fr, 0.4)
    if C.get("box_cols"):
        vc = [vc[i] for i in C["box_cols"]]
    L, R = vc[0], vc[-1]
    if C.get("box_rows"):
        hr = [hr[i] for i in C["box_rows"]]
    line = hr[0] if C["x_tick_line"] == "top" else hr[-1]
    side = +1 if C["x_tick_line"] == "top" else -1
    xs = sorted(k.line_stubs(fr, line, side, L + 15, R - 15, length=C.get("tick_len", 12), half=C.get("half", 3)))
    if len(xs) > len(C["x_ticks"]) and len(C["x_ticks"]) > 2:
        xs = k.even_subset(xs, len(C["x_ticks"])) or xs
    if len(xs) != len(C["x_ticks"]):
        raise RuntimeError(f"x ticks: expected {len(C['x_ticks'])}, found {xs}")
    xm = list(zip(sorted(xs), C["x_ticks"]))
    if C.get("x_spines"):
        xm = [(L, C["x_spines"][0])] + xm + [(R, C["x_spines"][1])]
    X = k.Lin(xm)
    spine = L if C["y_tick_spine"] == "left" else R
    yside = +1 if C["y_tick_spine"] == "left" else -1
    lo_r = hr[0] + 10 if C.get("y_top_box", True) else 0
    ys = sorted(k.spine_stubs(fr, spine, yside, lo_r, image.shape[0] - 1, length=C.get("tick_len", 12), half=C.get("half", 3)),
                reverse=True)
    ys = [y for y in ys if y < C.get("y_max_row", 1e9)]
    sub = k.even_subset(ys, len(C["y_ticks"])) if len(ys) > len(C["y_ticks"]) else ys
    if not sub or len(sub) != len(C["y_ticks"]):
        raise RuntimeError(f"y ticks: expected {len(C['y_ticks'])}, found {ys}")
    ym = list(zip(sorted(sub, reverse=True), C["y_ticks"]))
    series = {n: k.color_mask(image, col, C.get("tol", 40)) for n, col in C["colors"].items()}
    overlap = k.color_mask(image, C["overlap"], C.get("tol", 40)) if C.get("overlap") else None
    outline = k.dark_mask(image, 90)
    c0, c1 = int(L) + 4, int(R) - 3
    if C.get("y_base_zero"):
        anyf = overlap.copy() if overlap is not None else np.zeros(outline.shape, bool)
        for m in series.values():
            anyf |= m
        ym.append((k.base_row_of(anyf[:, c0:c1]), 0.0))
    Y = k.Lin(ym)
    if C.get("exclude"):  # regions (c0, r0, c1, r1) covered by an inset, read as no face
        for a, b, c, d in C["exclude"]:
            for m in list(series.values()) + ([overlap] if overlap is not None else []) + [outline]:
                m[int(b):int(d), int(a):int(c)] = False
    out = k.histogram(X, Y, series, overlap, outline, c0, c1,
                      note=f"x misfit {X.misfit_px:.2g} px")
    keep = C.get("keep")
    return [p for p in out if keep is None or p["series"] == keep]
