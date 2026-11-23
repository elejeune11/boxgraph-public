"""Supp. Fig. 6b: total bead displacement against initial distance from the cell, one colour per cell
(red, green, blue), soft hydrogel (left panel) and soft fibre network (right panel).
Axes from the tick marks of the thick black axis lines. Markers are blobs of the cell's colour; only
blobs the size and shape of one whole marker (area within 25% of the panel's median single-marker
area, about round) are read: beads whose markers overlap others of the same or another colour are
left out, so a reading holds a subset of the beads, not all of them. Each point is (distance,
displacement) at the blob's centre, +/- 2 px plus the axis misfit."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

COLOURS = {"red": (237, 28, 36), "green": (0, 240, 0), "blue": (0, 0, 240)}


def read_cell(image, colour, yticks, xticks):
    ink = K.dark(image, 110.0)
    yl, xl = K.frame(ink)
    yax = K.y_axis(ink, yl, yticks)
    # markers drawn over the x axis line cut its longest run short: look for ticks along the whole row
    W = ink.shape[1]
    xt = sorted(p for p in K.side_ticks(ink, (xl[0], xl[1], yl[0], W - 31), "x", +1) if p >= yl[0] - 3)
    xax = K.Axis(xt, xticks, what=f"x ticks {[round(p) for p in xt]}")
    # the size of one marker: the commonest blob area over all three colours
    areas = []
    per = {}
    for name, rgb in COLOURS.items():
        m = K.near(image, rgb, 90)
        m[xl[0]:, :] = False
        per[name] = K.blobs(m, open_px=5, min_area=100)
        areas += [b[4] for b in per[name]]
    single = float(np.median(areas))
    out = []
    for col, row, h, w, area in per[colour]:
        if not (0.75 * single <= area <= 1.25 * single) or not (0.8 <= h / w <= 1.25):
            continue
        # a marker partly covered by another loses area and its centre shifts by up to the lost part
        p = 2.0 + yax.misfit + max(0.0, 1.0 - area / single) * float(np.sqrt(single / np.pi))
        out.append({"x": round(xax.to_val(col), 2) + 0.0, "y": yax.to_val(row), "lo": yax.to_val(row + p),
                    "hi": yax.to_val(row - p), "px": [col, row], "px_lo": row + p, "px_hi": row - p,
                    "note": f"single marker ({area} px, median single {single:.0f}); y misfit {yax.misfit:.1f} px, "
                            f"x misfit {xax.misfit:.1f} px"})
    out.sort(key=lambda r: r["x"])
    return out


def read_panel(image, yticks, xticks):
    """All three cells' single markers, sorted by distance; each note names the cell's colour."""
    out = []
    for name in COLOURS:
        for r in read_cell(image, name, yticks, xticks):
            r["note"] = f"{name} cell; " + r["note"]
            out.append(r)
    out.sort(key=lambda r: (r["x"], r["y"]))
    return out
