"""Expt / CFD column pairs (Figs. 3f and 4f): the categories alternate Expt (bead tracking), CFD for networks
1, 2, 3. A reading of one kind at network n reads category 2n - 1 (Expt) or 2n (CFD) and reports x = n."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_cols", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cols.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read_pair(image, at, box, labels, kind, capfrac):
    cal = C.calibrate(image, box, labels, True)
    out = []
    for n in at:
        k = 2 * int(round(n)) - (1 if kind == "expt" else 0)
        rec = C.read_column(image, [k], cal, with_caps=True, capfrac=capfrac)[0]
        rec["x"] = n
        rec["note"] = f"network {int(round(n))} {kind}: " + rec["note"]
        out.append(rec)
    return out
