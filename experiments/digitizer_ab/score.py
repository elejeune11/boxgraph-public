"""Scoring a figure reading against ground truth."""

from __future__ import annotations

import math


def _u(v: float, truth: dict) -> float:
    return math.log10(v) if truth["scale"] == "log10" else v


def _span(truth: dict) -> float:
    a, b = truth["span"]
    return _u(b, truth) - _u(a, truth)


def normalized(y: float, t: float, truth: dict) -> float:
    """|y - t| as a fraction of the axis span (in decades on a log axis)."""
    if truth["scale"] == "log10" and (y is None or y <= 0):
        return math.inf
    return abs(_u(y, truth) - _u(t, truth)) / _span(truth)


def _match(answer: dict, truth: dict) -> list[dict | None]:
    rows = [r for r in (answer or {}).get("readings", []) if r.get("x") is not None]
    out = []
    for x in truth["at"]:
        near = [r for r in rows if abs(float(r["x"]) - x) <= 0.05 * (1 + abs(x))]
        out.append(min(near, key=lambda r: abs(float(r["x"]) - x)) if near else None)
    return out


def score_run(answer: dict, truth: dict) -> dict:
    errs, covered, widths, missing = [], 0, [], 0
    for r, t in zip(_match(answer, truth), truth["y"]):
        if r is None or r.get("y") is None:
            missing += 1
            continue
        y = float(r["y"])
        errs.append(normalized(y, t, truth))
        lo, hi = r.get("lo"), r.get("hi")
        if lo is not None and hi is not None:
            lo, hi = min(float(lo), float(hi)), max(float(lo), float(hi))
            covered += lo <= t <= hi
            if truth["scale"] == "log10" and lo <= 0:
                widths.append(math.inf)
            else:
                widths.append((_u(hi, truth) - _u(lo, truth)) / _span(truth))
    n = len(truth["at"])
    return {
        "mean_err": sum(errs) / len(errs) if errs else math.nan,
        "max_err": max(errs) if errs else math.nan,
        "coverage": covered / n,
        "mean_width": sum(widths) / len(widths) if widths else math.nan,
        "missing": missing,
    }


def consistency(a: dict, b: dict, truth: dict) -> float:
    """Mean difference between two runs' values, as a fraction of the axis."""
    ds = []
    for ra, rb in zip(_match(a, truth), _match(b, truth)):
        if ra is None or rb is None or ra.get("y") is None or rb.get("y") is None:
            continue
        ds.append(normalized(float(ra["y"]), float(rb["y"]), truth))
    return sum(ds) / len(ds) if ds else math.nan
