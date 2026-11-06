# Ursino 1998, steady state of the carotid baroreflex (Eqs. 30-42) for a constant,
# nonpulsatile carotid sinus pressure Pcs (open loop). At steady state Eq. 30 gives
# P~ = Pcs; Eq. 31 gives fcs; Eqs. 33-34 give fes, fev; Eqs. 35-37 give each effector as
# theta0 + G ln(fes - fes,min + 1) (0 below fes,min); Eqs. 38-42 give T.
# Ports: mmHg, ml, s, 1/s (spikes/s). The log term is taken of the number of spikes/s.
import math

EFFECTORS = [("Emax_lv", "G_Emax_lv", "Emax_lv0"), ("Emax_rv", "G_Emax_rv", "Emax_rv0"),
             ("R_sp", "G_R_sp", "R_sp0"), ("R_ep", "G_R_ep", "R_ep0"),
             ("Vu_sv", "G_Vu_sv", "Vu_sv0"), ("Vu_ev", "G_Vu_ev", "Vu_ev0")]


def steady(p, Pcs):
    e = math.exp((Pcs - p["Pn"]) / p["ka"])
    fcs = (p["fmin"] + p["fmax"] * e) / (1.0 + e)                       # Eq. 31
    fes = p["fes_inf"] + (p["fes0"] - p["fes_inf"]) * math.exp(-p["kes"] * fcs)  # Eq. 33
    e2 = math.exp((fcs - p["fcs0"]) / p["kev"])
    fev = (p["fev0"] + p["fev_inf"] * e2) / (1.0 + e2)                  # Eq. 34
    lg = math.log(fes - p["fes_min"] + 1.0) if fes >= p["fes_min"] else 0.0  # Eqs. 35, 38
    out = {name: p[th0] + p[g] * lg for name, g, th0 in EFFECTORS}     # Eqs. 36-37
    out["T"] = p["G_T_s"] * lg + p["G_T_v"] * fev + p["T0"]            # Eqs. 39-42
    out["fcs"], out["fes"], out["fev"] = fcs, fes, fev
    return out


def run(inputs, settings):
    o = steady(inputs, inputs["Pcs"])
    return {k: o[k] for k in ["Emax_lv", "Emax_rv", "R_sp", "R_ep", "Vu_sv", "Vu_ev", "T",
                              "fcs", "fes", "fev"]}
