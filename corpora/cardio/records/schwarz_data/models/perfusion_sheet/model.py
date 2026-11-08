# Adapter (software: true): the released per-territory perfusion values (hemodynamics_hum06.xlsx,
# sheet 'perfusion': one column per myocardial region, row 1 the region labels, then one value per
# perfusion territory, in ml/min/g as the paper reports perfusion). Our own code pools every value
# of the sheet (all regions, including 'bg') and returns their number, median and quartiles.
# Quartiles: settings.percentile_method 'linear' (numpy's default) or 'matlab' (Matlab prctile:
# the k-th of n sorted values sits at the (k - 0.5)/n quantile). The paper does not say which it used.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_data_xlsx", os.path.join(_HERE, "..", "hemodynamics_workbook", "_xlsx.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)


def _q(v, p, method):
    if method == "linear":
        return float(np.percentile(v, p))
    if method == "matlab":
        n = len(v)
        pos = np.arange(1, n + 1) - 0.5
        return float(np.interp(p / 100.0 * n, pos, v))
    raise ValueError(f"unknown percentile_method {method!r}")


def run(inputs, settings):
    cells = X.sheet(X.source_file(settings["file"]), settings["sheet"])
    v = np.sort([val for (c, r), val in cells.items() if r >= 2 and isinstance(val, float)])
    m = settings["percentile_method"]
    return {"n": float(len(v)), "median": _q(v, 50, m), "p25": _q(v, 25, m), "p75": _q(v, 75, m)}
