"""Applying a recorded figure reading to an image: the one function the build
and the `boxgraph figure` commands share."""

from __future__ import annotations

from pathlib import Path

from . import digitize as D
from . import precision as P
from .schema import FigureReading


def _from_code(fr: FigureReading, img, code_reader, res: dict, overlay_to) -> dict:
    """A reading by the record's own code: run it, check what it returns, draw it."""
    if code_reader is None:
        res["errors"].append(f"figure {fr.id}: mode code needs its code file (`code`)")
        return res
    try:
        at = [P.parse(t).value for t in fr.at]
        raw = code_reader(img, at)
    except Exception as e:  # noqa: BLE001  (the reader's code may raise anything)
        res["errors"].append(f"figure {fr.id}: its code failed: {e}")
        return res
    rows = []
    for i, r in enumerate(raw):
        x, y = r.get("x"), r.get("y")
        found = bool(r.get("found", y is not None)) and y is not None
        row = {"x": x, "y": y if found else None, "lo": r.get("lo") if found else None,
               "hi": r.get("hi") if found else None, "found": found, "note": str(r.get("note", ""))}
        for k in ("bar_lo", "bar_hi", "bar_lo_outer", "bar_hi_outer"):
            if r.get(k) is not None:
                row[k] = r[k]
        if not isinstance(x, (int, float)):
            res["errors"].append(f"figure {fr.id}: reading {i} has no numeric x")
            continue
        if found:
            if row["lo"] is None or row["hi"] is None or not (row["lo"] <= y <= row["hi"]):
                res["errors"].append(f"figure {fr.id}: x = {x:g}: needs an interval lo <= y <= hi")
            px = r.get("px")
            if not (isinstance(px, list) and len(px) == 2):
                res["errors"].append(f"figure {fr.id}: x = {x:g}: no pixel position `px` [column, row], so it "
                                     f"cannot be checked on the overlay")
            else:
                row["px"] = [float(px[0]), float(px[1])]
                if r.get("px_lo") is not None and r.get("px_hi") is not None:
                    row["px_span"] = [float(r["px_lo"]), float(r["px_hi"])]
        elif not row["note"]:
            row["note"] = "not found"
        rows.append(row)
    res["readings"] = rows
    for r in rows:
        if not r["found"]:
            res["errors"].append(f"figure {fr.id}: x = {r['x']:g}: {r['note']}")
    if overlay_to is not None:
        Path(overlay_to).parent.mkdir(parents=True, exist_ok=True)
        res["overlay"] = str(D.overlay_px(img, rows, overlay_to))
    return res


def apply(fr: FigureReading, img, overlay_to: str | Path | None = None, code_reader=None) -> dict:
    """Read the figure in `img` (the rendered crop) as `fr` says. Returns a dict
    with readings, errors, notes, residual_px and, if asked, the overlay path.
    A reading in code mode calls `code_reader(img, at)`, which runs the record's code."""
    res: dict = {"id": fr.id, "where": fr.where, "what": fr.what, "page": fr.page, "readings": [], "errors": [],
                 "notes": []}
    if fr.mode == "code":
        return _from_code(fr, img, code_reader, res, overlay_to)
    res["skew_deg"] = D.find_skew(img)
    img = D.deskew(img)  # marks and seeds are positions in the straightened crop
    try:
        xa = D.Axis(fr.x.scale, [(p, P.parse(t).value) for p, t in fr.x.marks])
        ya = D.Axis(fr.y.scale, [(p, P.parse(t).value) for p, t in fr.y.marks])
    except (D.CalibrationError, P.PrintedError) as e:
        res["errors"].append(str(e))
        return res
    res["residual_px"] = [xa.residual_px, ya.residual_px]
    try:
        if fr.mode == "curve":
            rs = D.read_curve(img, xa, ya, [P.parse(t).value for t in fr.at], fr.color, fr.tol, box=fr.box, seed=fr.seed)
        elif fr.mode == "bars":
            rs = D.read_bars(img, xa, ya, fr.color, fr.tol, box=fr.box, error_bars=fr.error_bars is not None,
                             bar_color=fr.bar_color)
        else:
            rs = D.read_markers(img, xa, ya, fr.color, fr.tol, box=fr.box, min_area=fr.min_area, max_area=fr.max_area,
                                error_bars=fr.error_bars is not None, bar_color=fr.bar_color)
    except P.PrintedError as e:
        res["errors"].append(str(e))
        return res
    res["readings"] = [{"x": r.x, "y": r.y, "lo": r.lo, "hi": r.hi, "found": r.found, "note": r.note,
                        **({"bar_lo": r.bar_lo, "bar_hi": r.bar_hi, "bar_lo_outer": r.bar_lo_outer,
                            "bar_hi_outer": r.bar_hi_outer} if r.bar_lo is not None else {})} for r in rs]
    if fr.error_bars is not None:
        res["error_bars"] = fr.error_bars
    for r in rs:
        if not r.found:
            res["errors"].append(r.note)
        elif r.note.startswith("ambiguous"):
            res["notes"].append(f"x = {r.x:g}: {r.note}")
    if overlay_to is not None:
        Path(overlay_to).parent.mkdir(parents=True, exist_ok=True)
        res["overlay"] = str(D.overlay(img, rs, xa, ya, overlay_to))
    return res
