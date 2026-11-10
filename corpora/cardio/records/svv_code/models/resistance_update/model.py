"""Adapter: runs the released code's own update_resistance and update_radii (svv/tree/utils/c_update.py,
loaded from the code folder BOXGRAPH_SOURCE; the module needs only numpy) on one bifurcation: a parent
with two terminal daughters a and b, written into svv's tree table (31 columns: 15/16 left/right child,
17 parent, 20 length, 21 radius, 22 flow, 23/24 left/right ratio, 25 reduced resistance, 26 depth) with
svv's connectivity array (left, right, parent; root.py line 265). Ports in cgs and mmHg; the function is
given mu in poise (svv passes nu * rho there, root.py line 266) and pressures in dyn/cm^2.

Outputs: R* of the parent and the two ratios svv writes; the Eq. S6 identity beta_a^gamma + beta_b^gamma;
the parent diameter svv writes by Eq. S8; and the pressure at the end of each daughter, P_root minus the
Hagen-Poiseuille drops (Eqs. S1-S2) along parent and daughter with the radii svv wrote (our arithmetic)."""
import importlib.util
import math
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
MMHG = 1333.22387415          # dyn/cm^2 per mmHg


def _find(*parts):
    d = _HERE
    for _ in range(10):
        cand = os.path.join(d, *parts)
        if os.path.exists(cand):
            return cand
        d = os.path.dirname(d)
    raise FileNotFoundError(os.path.join(*parts))


def _c_update():
    src = os.environ.get("BOXGRAPH_SOURCE")
    src = os.path.abspath(src) if src and os.path.isdir(src) else _find("corpus", "cardio", "code", "svv_code")
    spec = importlib.util.spec_from_file_location("svv_c_update", os.path.join(src, "svv", "tree", "utils", "c_update.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(inputs, settings):
    cu = _c_update()
    mu = inputs["mu"] / 100.0                                   # cP -> poise
    gamma = inputs["gamma"]
    P_root, P_term = inputs["P_root"] * MMHG, inputs["P_term"] * MMHG
    # update_resistance computes max_depth once and never lowers it (c_update.py lines 6-12), so on a
    # table with vessels at two depths it never ends (q_update_resistance_loop). It is therefore called
    # on the same bifurcation laid out daughters first (rows 0, 1) and parent last (row 2), every depth
    # equal: its single pass then visits the daughters before the parent, as its depth order means to.
    up = np.full((3, 31), np.nan)
    up[2, 15], up[2, 16] = 0.0, 1.0
    up[0, 17] = up[1, 17] = 2.0
    up[:, 20] = [inputs["l_a"], inputs["l_b"], inputs["l_p"]]
    up[:, 22] = [inputs["Q_a"], inputs["Q_b"], inputs["Q_a"] + inputs["Q_b"]]   # Eq. S3
    up[:, 26] = 0.0
    cu.update_resistance(up, np.nan_to_num(up[:, 15:18], nan=-1.0).astype(np.int64), gamma, mu)
    # back to svv's layout, root first, for update_radii
    data = up[[2, 0, 1], :].copy()
    data[0, 15], data[0, 16], data[0, 17] = 1.0, 2.0, np.nan
    data[1, 17] = data[2, 17] = 0.0
    data[:, 26] = [0.0, 1.0, 1.0]
    idx = np.nan_to_num(data[:, 15:18], nan=-1.0).astype(np.int64)
    # update_radii reads the parent of vessel i from idx[i, 3]; svv's connectivity has three columns
    # (root.py line 265), so the parent column is appended for the daughters to be reached
    idx4 = np.hstack([idx, idx[:, 2:3]])
    cu.update_radii(data, idx4, P_root, P_term)
    r = data[:, 21]

    def drop(i):
        return 8.0 * mu * data[i, 20] * data[i, 22] / (math.pi * r[i] ** 4)
    return {"Rstar_p": float(data[0, 25]), "beta_a": float(data[0, 23]), "beta_b": float(data[0, 24]),
            "beta_sum": float(data[0, 23] ** gamma + data[0, 24] ** gamma),
            "d_p": float(2e4 * r[0]),
            "P_end_a": float((P_root - drop(0) - drop(1)) / MMHG),
            "P_end_b": float((P_root - drop(0) - drop(2)) / MMHG)}
