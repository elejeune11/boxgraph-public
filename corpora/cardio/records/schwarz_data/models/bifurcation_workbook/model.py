# Adapter (software: true): the branching statistics behind Figs. 2-4, recomputed from the individual
# data points of 'final_tree_bifurcation_summary_all-ld.xlsx' (guide lines 234-246). Our own code
# (streaming reader in ../stochastic_table2/_xlsx_stream.py). Sheets used:
#   segsPerDiam   B nSegments, C nMothers per class (rows 2-11, Table 1's classes)
#   furctype      A nConnect, B n (rows 2-6)
#   length all mm  one length per element (mm)
#   length dclass  one column per class (A-J), lengths in mm
#   symmetry       one column per mother class (A-J), daughter symmetry
#   area           two columns per mother class: '<class>, sym 0.50-1.00' then '<class>, sym 0.00-0.50'
#   moth diam - daught symmetry  A mother diameter (m), B symmetry, all one-mother nodes
# The class is chosen by its lower bound d (settings class_edges_um gives the column order).
# The large-vessel area growth uses the '>= 400 um' columns of 'area' (both symmetry groups pooled): the
# sheet holds no mother diameters, so 'larger than 400 um' (p. 5) is taken as the >= 400 um class.
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_xlsx_stream", os.path.join(_HERE, "..", "stochastic_table2", "_xlsx_stream.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)
_CACHE = {}
_LET = [chr(65 + i) for i in range(26)]


def _book(name):
    if name not in _CACHE:
        b = X.Book(name)
        _CACHE[name] = {
            "segs": b.cells("segsPerDiam"),
            "furc": b.cells("furctype"),
            "len_all": b.columns("length all mm", first_row=1),
            "len": b.columns("length dclass"),
            "sym": b.columns("symmetry"),
            "area": b.columns("area"),
            "md": b.columns("moth diam - daught symmetry"),
        }
    return _CACHE[name]


def run(inputs, settings):
    w = _book(settings["file"])
    edges = settings["class_edges_um"]
    k = [i for i, e in enumerate(edges) if abs(e - inputs["d"]) < 1e-6 * e][0]
    out = {
        "n_segments": float(w["segs"][("B", k + 2)]),
        "n_mothers": float(w["segs"][("C", k + 2)]),
    }
    L = w["len"][_LET[k]] * 1e3                      # mm -> um
    out["n_length"] = float(len(L))
    out["L_median"] = float(np.median(L))
    S = w["sym"][_LET[k]]
    out["n_sym"] = float(len(S))
    out["S_median"] = float(np.median(S))
    hi, lo = w["area"][_LET[2 * k]], w["area"][_LET[2 * k + 1]]
    out.update({"n_area_hi": float(len(hi)), "n_area_lo": float(len(lo)),
                "A_median_hi": float(np.median(hi)), "A_median_lo": float(np.median(lo))})
    f = w["furc"]
    n = {int(f[("A", r)]): f[("B", r)] for r in range(2, 20) if isinstance(f.get(("A", r)), float)}
    tot = sum(n.values())
    out["pct_3"] = 100.0 * n.get(3, 0) / tot
    out["pct_4"] = 100.0 * n.get(4, 0) / tot
    out["pct_more"] = 100.0 * sum(v for c, v in n.items() if c > 4) / tot
    out["n_internal_nodes"] = float(tot)
    out["n_length_all"] = float(len(w["len_all"]["A"]))
    out["L_median_all"] = float(np.median(w["len_all"]["A"])) * 1e3
    dM, Sm = w["md"]["A"], w["md"]["B"]
    out["n_pairs"] = float(len(dM))
    out["S_median_large"] = float(np.median(Sm[dM > inputs["d_S_large"] * 1e-6]))
    top = len(edges) - 1
    out["A_median_top_class"] = float(np.median(np.r_[w["area"][_LET[2 * top]], w["area"][_LET[2 * top + 1]]]))
    return out
