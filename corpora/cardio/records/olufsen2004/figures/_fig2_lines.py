"""Fig. 2 (PDF p. 8): reading one horizontal time-scale line. Calibration in _fig2.py.

The lines are told apart from the image: by colour (red for flow, green for pressure time-scales,
as the caption says) and by their order from the top among the lines of that colour, and each
reading reports the line's style (the fraction of columns it covers: solid near 1, dashed or
dash-dot less) so it can be matched to the legend sample (solid, dashed, dash-dot).
At each x the line's centre is the median centre of its coloured runs over the columns within
SEARCH of that x, skipping columns where the blue curve crosses. The interval adds the y
calibration misfit, one pixel of placement and the spread of the centres over those columns.
"""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location("_fig2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

SEARCH = 80  # columns either side


def _levels(mask, cols, r0, r1):
    """Centres of the horizontal lines of a mask over these columns, top to bottom, with coverage."""
    prof = mask[r0:r1, cols].mean(axis=1)
    rows = np.nonzero(prof > 0.15)[0]
    if rows.size == 0:
        return []
    cuts = np.nonzero(np.diff(rows) > 3)[0]
    starts = np.r_[rows[0], rows[cuts + 1]]
    ends = np.r_[rows[cuts], rows[-1]]
    return [((s + e) / 2 + 0.5 + r0, float(prof[s:e + 1].max())) for s, e in zip(starts, ends)]


def read_line(image, at, which, rank):
    cal = _f.calibrate(image)
    mask = _f.colour(image, which)
    blue = _f.colour(image, "blue")
    left, top, right, bot = cal["box"]
    out = []
    for x in at:
        x = float(x)
        c = int(round(_f.col_of(cal, x) - 0.5))
        cols = np.arange(max(c - SEARCH, left + 3), min(c + SEARCH, right - 3))
        lv = _levels(mask, cols, top + 2, bot - 1)
        if len(lv) <= rank:
            out.append({"x": x, "y": None, "note": f"fewer than {rank + 1} {which} lines here"})
            continue
        level, coverage = lv[rank]
        band = (int(level) - 12, int(level) + 13)
        cen = []
        for q in cols:
            if blue[band[0]:band[1], q].any():
                continue  # the blue curve crosses here
            rr = np.nonzero(mask[band[0]:band[1], q])[0]
            if rr.size:
                cen.append(band[0] + (rr.min() + rr.max()) / 2 + 0.5)
        cen = np.array(cen)
        row = float(np.median(cen))
        half_px = cal["ymis"] + 1.0 + float(np.max(np.abs(cen - row)))
        style = "solid" if coverage > 0.9 else "broken (dashed or dash-dot)"
        out.append({"x": x, "y": float(_f.val_of_row(cal, row)),
                    "lo": float(_f.val_of_row(cal, row + half_px)), "hi": float(_f.val_of_row(cal, row - half_px)),
                    "px": [c + 0.5, row], "px_lo": row - half_px, "px_hi": row + half_px,
                    "note": f"{which} line {rank + 1} from the top, {style} (covers {coverage:.2f} of columns), "
                            f"{cen.size} columns"})
    return out
