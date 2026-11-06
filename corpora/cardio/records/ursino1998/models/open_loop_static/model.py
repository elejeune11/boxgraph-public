# Fig. 7 (p. 8): open-loop static responses. circulation_baroreflex (Eqs. 1-42) is run with the
# carotid sinus pressure held at a constant (its Pcs_open hook) until settled, at Pcs = Pcs_n * P_norm
# and at Pcs = P_norm; SAP, CO and the total systemic resistance Rsa + (Rsp + Rsv)||(Rep + Rev) (as in
# reflex_range) are returned as ratios of the two. Vagotomy (fev = 0) is G_T_v = 0 in the inputs.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_baroreflex", os.path.join(_here, "..", "circulation_baroreflex", "model.py"))
_cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cb)


def _sim(p, pcs, settings):
    q = dict(p)
    q["Pcs_open"] = pcs
    return _cb._simulate(q, settings, None)


def _rtot(p, m):
    a = m["Rsp"] + p["R_sv"]
    b = m["Rep"] + p["R_ev"]
    return p["R_sa"] + a * b / (a + b)


def run(inputs, settings):
    p = dict(inputs)
    x = p.pop("Pcs_n")
    pn = p.pop("P_norm")
    m = _sim(p, x * pn, settings)
    m0 = _sim(p, pn, settings)
    return {"SAP_n": m["Psa"] / m0["Psa"], "CO_n": m["CO"] / m0["CO"], "R_n": _rtot(p, m) / _rtot(p, m0)}
