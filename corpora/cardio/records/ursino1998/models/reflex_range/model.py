# Static reflex changes between two constant carotid sinus pressures (open loop, no
# pulsation), from the steady state of Eqs. 30-42 (reflex_static). The quantities are the
# ones the paper says the effector gains were set to reproduce (pp. 4-5):
#   dEmax  = (Emax,lv(P_low) - Emax,lv(P_high)) / Emax,lv basal           [percent]
#   dR_sp  = (Rsp(P_low) - Rsp(P_high)) / Rsp(P_high)                       [percent]
#   dR_tot = (R(P_low) - R(P_high)) / R(P_high), R = Rsa + (Rsp+Rsv)||(Rep+Rev) [percent]
#   dVu_tot = |Vu,sv + Vu,ev change| / body mass, dVu_sv = |Vu,sv change| / mass [ml/kg]
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_reflex_static", os.path.join(_here, "..", "reflex_static", "model.py"))
_rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rs)


def _total(p, o):
    a = o["R_sp"] + p["R_sv"]
    b = o["R_ep"] + p["R_ev"]
    return p["R_sa"] + a * b / (a + b)


def run(inputs, settings):
    p = inputs
    lo = _rs.steady(p, p["P_low"])
    hi = _rs.steady(p, p["P_high"])
    return {
        "dEmax": 100.0 * (lo["Emax_lv"] - hi["Emax_lv"]) / p["Emax_lv_basal"],
        "dR_sp": 100.0 * (lo["R_sp"] - hi["R_sp"]) / hi["R_sp"],
        "dR_tot": 100.0 * (_total(p, lo) - _total(p, hi)) / _total(p, hi),
        "dVu_tot": abs((lo["Vu_sv"] + lo["Vu_ev"]) - (hi["Vu_sv"] + hi["Vu_ev"])) / p["M"],
        "dVu_sv": abs(lo["Vu_sv"] - hi["Vu_sv"]) / p["M"],
    }
