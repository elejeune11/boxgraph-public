# Adapter (software: true): the released per-diameter-class medians of the network hemodynamics
# (hemodynamics_hum06.xlsx, sheets 'pressure' (mmHg), 'flow' (ml/min), 'wss' (Pa); column A the
# class diameter in um). settings.column picks the median: 'B' (median pooled) or 'E' (median
# smoothed). Our own code then reads, from those class medians:
#   P, Q    the pressure and flow medians of the class whose diameter is nearest d;
#   d_class that class's diameter;
#   wss_below the median of the shear-stress class medians of all classes below d_cut;
#   d_wss_peak the diameter of the class with the largest shear-stress median.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_data_xlsx", os.path.join(_HERE, "..", "hemodynamics_workbook", "_xlsx.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)


def _curve(path, sheet, col):
    cells = X.sheet(path, sheet)
    d, y = X.column(cells, "A"), X.column(cells, col)
    keep = [(a, b) for a, b in zip(d, y) if a is not None and b is not None]
    return np.array([a for a, _ in keep]), np.array([b for _, b in keep])


def run(inputs, settings):
    path = X.source_file(settings["file"])
    col = settings["column"]
    dP, P = _curve(path, "pressure", col)
    dQ, Q = _curve(path, "flow", col)
    dW, W = _curve(path, "wss", col)
    iP = int(np.argmin(np.abs(dP - inputs["d"])))
    iQ = int(np.argmin(np.abs(dQ - inputs["d"])))
    if dP[iP] != dQ[iQ]:
        raise ValueError("the pressure and flow sheets have different diameter classes")
    return {
        "P": float(P[iP]),
        "Q": float(Q[iQ]),
        "d_class": float(dP[iP]),
        "wss_below": float(np.median(W[dW < inputs["d_cut"]])),
        "d_wss_peak": float(dW[int(np.argmax(W))]),
    }
