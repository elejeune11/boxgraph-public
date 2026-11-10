# Our code (software: true only to read the released workbook from $BOXGRAPH_SOURCE): Table 2 of
# schwarz2020 recomputed from the per-element sheets of 'Gdistal variations.xlsx' (guide lines 254-261):
#   <X>median  per element (rows 2-202185: TreeQ.IE in order, then TreeQ.SE): A median and B mean over
#              the 1000 stochastic simulations; deterministic runs with the distal conductance taken as
#              C the median, D the mean, E the power fit of the in silico distribution
#   <X>_CoV, <X>_mad  per element, one column per diameter class (Table 1's classes)
# for X = P (mmHg), Q (ml/min, signed), WSS (Pa, signed).
# Table 2's columns, as we read its legend (p. 10):
#   CV, MAD: median and 95th percentile over all elements of the per-element CoV and MAD
#   Agreement with median: Pearson's r and the unstandardized slope beta of the least-squares line
#   A = beta X + c of the stochastic median A on the deterministic run X (E 'power fit', C 'median G')
# Also the deterministic values at a few elements, to set against the stored network solution:
#   P at IE(1) (row 2) and SE(1) (row 101225), Q at the inlets SE(100960) LCX (row 202184) and
#   SE(100961) LAD (row 202185). Pressures converted to Pa with 133.32 Pa/mmHg (the release's factor).
import importlib.util
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("schwarz_xlsx_stream", os.path.join(_HERE, "_xlsx_stream.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)

ROW_IE1, ROW_SE1, ROW_LCX, ROW_LAD = 2, 101225, 202184, 202185


def run(inputs, settings):
    book = X.Book(settings["file"])
    pm = settings["percentile_method"]
    out = {}
    for var in ("P", "Q", "WSS"):
        med = book.columns(var + "median")
        cv = np.concatenate([v for _, v in sorted(book.columns(var + "_CoV").items())])
        mad = np.concatenate([v for _, v in sorted(book.columns(var + "_mad").items())])
        out[var + "_cv_median"] = X.percentile(cv, 50, pm)
        out[var + "_cv_p95"] = X.percentile(cv, 95, pm)
        out[var + "_mad_median"] = X.percentile(mad, 50, pm)
        out[var + "_mad_p95"] = X.percentile(mad, 95, pm)
        a = med["A"]
        for tag, col in (("fit", "E"), ("medG", "C")):
            x = med[col]
            out[f"{var}_pcc_{tag}"] = float(np.corrcoef(a, x)[0, 1])
            out[f"{var}_beta_{tag}"] = float(np.polyfit(x, a, 1)[0])
        out["n_elements_" + var] = float(len(a))
        if var == "P":
            for tag, col in (("medG", "C"), ("fit", "E")):
                out[f"P_IE1_{tag}"] = float(med[col][ROW_IE1 - 2]) * 133.32
                out[f"P_SE1_{tag}"] = float(med[col][ROW_SE1 - 2]) * 133.32
        if var == "Q":
            for tag, col in (("medG", "C"), ("fit", "E")):
                out[f"Q_LCX_{tag}"] = float(med[col][ROW_LCX - 2])
                out[f"Q_LAD_{tag}"] = float(med[col][ROW_LAD - 2])
    return out
