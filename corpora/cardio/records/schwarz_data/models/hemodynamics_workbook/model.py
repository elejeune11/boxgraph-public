# Adapter (software: true): reads one of the released hemodynamics workbooks from $BOXGRAPH_SOURCE
# and returns what the authors' own (unreleased) Matlab analysis wrote into it. Nothing is fitted
# here; the coefficients are the authors'. Our own code only finds the cells by their labels:
#   sheet 'fits', column B conductance, C flow, D pressure, F velocity;
#   row 'all power, slope' / 'all power, factor' / 'all power, R^2' (the non-linear power fits
#   y = factor * d^slope, d in m) and row 'all, slope' (the log-linear fit's slope);
#   sheet 'conductance', column H 'power fit' (the fitted line as tabulated against column A,
#   'diameter (um)'): its log-log slope is the exponent of the line the workbook plots;
#   number of diameter classes: rows with a number in column A of 'conductance' and of 'flow'.
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_data_xlsx", os.path.join(_HERE, "_xlsx.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)

_COLUMN = {"G": "B", "Q": "C", "P": "D", "v": "F"}


def _row(cells, label):
    rows = [r for (c, r), v in cells.items() if c == 1 and isinstance(v, str) and v.strip() == label]
    if len(rows) != 1:
        raise ValueError(f"sheet 'fits': {len(rows)} rows labelled {label!r}")
    return rows[0]


def _loglog_slope(d_um, y):
    pts = [(math.log10(d * 1e-6), math.log10(v)) for d, v in zip(d_um, y) if d and v and v > 0]
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    return sum((x - mx) * (z - my) for x, z in pts) / sum((x - mx) ** 2 for x, _ in pts)


def run(inputs, settings):
    path = X.source_file(settings["file"])
    fits = X.sheet(path, "fits")
    r_slope, r_factor = _row(fits, "all power, slope"), _row(fits, "all power, factor")
    r_r2, r_loglin = _row(fits, "all power, R^2"), _row(fits, "all, slope")
    out = {}
    for k, col in _COLUMN.items():
        out[f"{k}_b"] = X.cell(fits, f"{col}{r_slope}")
        out[f"{k}_a"] = X.cell(fits, f"{col}{r_factor}")
        out[f"{k}_r2"] = X.cell(fits, f"{col}{r_r2}")
    out["Q_b_loglin"] = X.cell(fits, f"C{r_loglin}")
    out["v_b_loglin"] = X.cell(fits, f"F{r_loglin}")
    g = X.sheet(path, "conductance")
    out["G_b_line"] = _loglog_slope(X.column(g, "A"), X.column(g, "H"))
    out["n_classes_G"] = float(sum(v is not None for v in X.column(g, "A")))
    q = X.sheet(path, "flow")
    out["n_classes_Q"] = float(sum(v is not None for v in X.column(q, "A")))
    return out
