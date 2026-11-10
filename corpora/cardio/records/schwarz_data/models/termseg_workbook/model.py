# Adapter (software: true): Table 1 as termseg_density.xlsx holds it (guide lines 248-253), read and
# recomputed by our own code (streaming reader in ../stochastic_table2/_xlsx_stream.py).
#   SegType  rows 2-11 per class: C distAll, D percAll, E distIE, F percIE, G distSE, H percSE; row 13 totals
#   Region   rows 2-11 per class: A, B, C density (n/cm^3) in sub-epicardium, mid-myocardium, sub-endocardium
#   diam per region, length per region  A epi, B mid, C endo: one value per terminal element (um)
# Density shares and region totals are computed here (100 rho / sum rho; sum over the classes); the
# region statistics (count, median and 10th/90th percentile of diameter, median length) from the values.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_xlsx_stream", os.path.join(_HERE, "..", "stochastic_table2", "_xlsx_stream.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)
_CACHE = {}
REG = {"epi": "A", "mid": "B", "endo": "C"}


def _book(name):
    if name not in _CACHE:
        b = X.Book(name)
        _CACHE[name] = {"seg": b.cells("SegType"), "reg": b.cells("Region"),
                        "diam": b.columns("diam per region"), "len": b.columns("length per region"),
                        "diam_cells": b.cells("diam per region")}
    return _CACHE[name]


def run(inputs, settings):
    w = _book(settings["file"])
    edges = settings["class_edges_um"]
    k = [i for i, e in enumerate(edges) if abs(e - inputs["d"]) < 1e-6 * e][0]
    r = k + 2
    s = w["seg"]
    out = {"n_all": s[("C", r)], "share_all": s[("D", r)], "n_internal": s[("E", r)],
           "n_terminal": s[("G", r)], "share_terminal": s[("H", r)],
           "n_all_total": s[("C", 13)], "n_internal_total": s[("E", 13)], "n_terminal_total": s[("G", 13)],
           "class_lo": s[("A", r)]}
    for name, col in REG.items():
        dens = [w["reg"][(col, rr)] for rr in range(2, 2 + len(edges))]
        out["dens_" + name] = dens[k]
        out["dshare_" + name] = 100.0 * dens[k] / sum(dens)
        out["dens_total_" + name] = float(sum(dens))
        d = w["diam"][col]
        out["n_" + name] = float(len(d))
        out["d_med_" + name] = float(np.median(d))
        out["d_p10_" + name] = float(np.percentile(d, 10))
        out["d_p90_" + name] = float(np.percentile(d, 90))
        out["l_med_" + name] = float(np.median(w["len"][col]))
    out["n_regions_stated"] = w["diam_cells"][("E", 3)]
    out["n_regions"] = out["n_epi"] + out["n_mid"] + out["n_endo"]
    return {k_: float(v) for k_, v in out.items()}
