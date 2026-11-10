# Adapter (software: true): 'Topology data.xlsx' (guide lines 229-233), read by our own code (streaming
# reader in ../stochastic_table2/_xlsx_stream.py), and Table 1's and the branching numbers recomputed from
# it, independently of the network file:
#   diameter-length  A element number (TreeQ.IE; + 1,000,000 for the source elements), B diameter (m),
#                    C length (m), from row 3
#   mother-daughter diams  A internal node, B-E upstream (mother) diameters, G-L downstream (daughter)
#                    diameters (m), flow-based, from row 3
# Per class (lower bound d, Table 1's classes with the release's edges, ../tree_table1/_tree.py): the
# number of elements. Whole sheet: counts, median and 10th/90th percentile of d, median l; nodes with one
# mother and two daughters: their number, median S = dS/dL for dM > d_S_large, median
# A = (dL^2 + dS^2)/dM^2 for dM > d_A_large, and the least-squares fit A = c_d dM + c_S S + c_0 over
# d_fit_lo <= dM <= d_fit_hi (dM in m).
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


X = _load("schwarz_xlsx_stream", os.path.join("..", "stochastic_table2", "_xlsx_stream.py"))
T = _load("schwarz_tree", os.path.join("..", "tree_table1", "_tree.py"))
_CACHE = {}


def _book(name):
    if name in _CACHE:
        return _CACHE[name]
    b = X.Book(name)
    ids, d, l = [], [], []
    for rn, r in b.rows("diameter-length"):
        if rn >= 3 and isinstance(r.get("A"), float):
            ids.append(r["A"]); d.append(r["B"]); l.append(r["C"])
    nm, dm, ds, dl = [], [], [], []
    n_rows = 0
    for rn, r in b.rows("mother-daughter diams"):
        if rn < 3 or not isinstance(r.get("A"), float):
            continue
        n_rows += 1
        mo = [r[c] for c in "BCDE" if isinstance(r.get(c), float)]
        da = sorted(r[c] for c in "GHIJKL" if isinstance(r.get(c), float))
        nm.append((len(mo), len(da)))
        if len(mo) == 1 and len(da) == 2:
            dm.append(mo[0]); ds.append(da[0]); dl.append(da[1])
    w = {"ids": np.array(ids), "d": np.array(d), "l": np.array(l), "n_node_rows": n_rows,
         "dM": np.array(dm), "dS": np.array(ds), "dL": np.array(dl)}
    _CACHE[name] = w
    return w


def run(inputs, settings):
    w = _book(settings["file"])
    d, l = w["d"], w["l"]
    out = {"n_rows": float(len(d)), "n_internal": float(np.sum(w["ids"] < 1e6)), "n_source": float(np.sum(w["ids"] >= 1e6))}
    c = T.classify(d, settings["class_edges_um"]) == T.class_index(inputs["d"], settings["class_edges_um"])
    out["n_class"] = float(c.sum())
    p10, _, med, _, p90 = T.stats(d * 1e6)
    out.update({"d_med": med, "d_p10": p10, "d_p90": p90, "l_med": T.stats(l * 1e6)[2]})
    dM, dS, dL = w["dM"], w["dS"], w["dL"]
    S, A = dS / dL, (dL ** 2 + dS ** 2) / dM ** 2
    out["n_node_rows"] = float(w["n_node_rows"])
    out["n_nodes"] = float(len(dM))
    out["S_median_large"] = T.stats(S[dM > inputs["d_S_large"] * 1e-6])[2]
    out["A_median_large"] = T.stats(A[dM > inputs["d_A_large"] * 1e-6])[2]
    f = (dM >= inputs["d_fit_lo"] * 1e-6) & (dM <= inputs["d_fit_hi"] * 1e-6)
    Xm = np.c_[dM[f], S[f], np.ones(f.sum())]
    coef, *_ = np.linalg.lstsq(Xm, A[f], rcond=None)
    out["c_d"], out["c_S"], out["c_0"] = float(coef[0]), float(coef[1]), float(coef[2])
    out["fit_r2"] = float(1 - np.sum((A[f] - Xm @ coef) ** 2) / np.sum((A[f] - A[f].mean()) ** 2))
    return out
