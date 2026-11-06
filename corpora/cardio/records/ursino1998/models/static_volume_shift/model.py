# Fig. 7 top (p. 8): blood volume shifted out of the splanchnic and extrasplanchnic beds when carotid
# sinus pressure falls from P_ref to P, "computed by maintaining constant venous pressures and flows".
# With venous pressure Pv and flow F held, the peripheral pressure is Pv + F Rp, so the bed's volume
# changes by dVu_v + C_p F dR_p (the venous stressed volume does not change). Effector values are
# the static steady state of Eqs. 35-37 (reflex_static). Ports: mmHg, ml, s, kg.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_reflex_static", os.path.join(_here, "..", "reflex_static", "model.py"))
_rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rs)


def run(inputs, settings):
    p = inputs
    a = _rs.steady(p, p["Pcs_n"] * p["P_norm"])
    r = _rs.steady(p, p["P_ref"])
    sp = (r["Vu_sv"] - a["Vu_sv"]) + p["C_sp"] * p["F_sp"] * (r["R_sp"] - a["R_sp"])
    ep = (r["Vu_ev"] - a["Vu_ev"]) + p["C_ep"] * p["F_ep"] * (r["R_ep"] - a["R_ep"])
    return {"shift_sp": sp / p["M"], "shift_ep": ep / p["M"]}
