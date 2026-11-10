# Closed-loop lumped-parameter circulation with LAD, LCx and RCA coronary territories
# (Yong et al. 2025, Eqs. 1-12, Fig. 1, Supp. Tables S1-S2), integrated with backward Euler
# at a fixed step as the paper states (Sec. 2.4). Flow statistics are those of Eqs. 13-14.
# Port units: mmHg, ml, s, mmHg*s/ml, ml/mmHg, mmHg/ml; outputs as declared in model.yaml.
# No I/O. The `dsfr` setting chooses Eq. 14 as printed ("integral") or the ratio of mean flows
# ("mean", used only by the variant model).
import math

import numpy as np

PI = math.pi
NODES = ("la", "lv", "ao", "sa", "sv", "ra", "rv", "pr", "pa", "pvn",
         "a_lad", "m_lad", "a_lcx", "m_lcx", "a_rca", "m_rca")
IX = {n: i for i, n in enumerate(NODES)}
TERR = ("lad", "lcx", "rca")


def e_ventricle(t, Tvc, Tvr):
    # Eq. 4
    if t <= Tvc:
        return 0.5 * (1.0 - math.cos(PI * t / Tvc))
    if t <= Tvc + Tvr:
        return 0.5 * (1.0 + math.cos(PI * (t - Tvc) / Tvr))
    return 0.0


def e_atrium(t, T, Tac, Tar, tac, tar):
    # Eq. 5
    if t <= tar + Tar - T:
        return 0.5 * (1.0 + math.cos(PI * (t + T - tar) / Tar))
    if t <= tac:
        return 0.0
    if t <= tac + Tac:
        return 0.5 * (1.0 - math.cos(PI * (t - tac) / Tac))
    return 0.5 * (1.0 + math.cos(PI * (t - tar) / Tar))


def r_micro(e, Rbar, k, frac, kph):
    # Eqs. 10-11 as printed: [(kPH sqrt(k Rbar) - sqrt(frac Rbar)) e + sqrt(frac Rbar)]^2
    # (kPH multiplies the square root, so Rmax = kPH^2 k Rbar)
    a = kph * math.sqrt(k * Rbar)
    b = math.sqrt(frac * Rbar)
    return ((a - b) * e + b) ** 2


class Circ:
    def __init__(self, p, settings):
        self.p = p
        self.vr = bool(settings.get("variable_resistance", True))
        self.imp = float(p["imp_ratio"]) if settings.get("imp", True) else 0.0

    def params_at(self, t):
        p = self.p
        tc = t % p["T"]
        ev_l = e_ventricle(tc, p["Tvc_lv"], p["Tvr_lv"])
        ev_r = e_ventricle(tc, p["Tvc_rv"], p["Tvr_rv"])
        ea_l = e_atrium(tc, p["T"], p["Tac_la"], p["Tar_la"], p["tac_la"], p["tar_la"])
        ea_r = e_atrium(tc, p["T"], p["Tac_ra"], p["Tar_ra"], p["tac_ra"], p["tar_ra"])
        E = {  # Eq. 3
            "lv": (p["Emax_lv"] - p["Emin_lv"]) * ev_l + p["Emin_lv"],
            "rv": (p["Emax_rv"] - p["Emin_rv"]) * ev_r + p["Emin_rv"],
            "la": (p["Emax_la"] - p["Emin_la"]) * ea_l + p["Emin_la"],
            "ra": (p["Emax_ra"] - p["Emin_ra"]) * ea_r + p["Emin_ra"],
        }
        Rm = {}
        for k in TERR:
            Rbar = p["Rm_" + k]
            if self.vr:
                if k == "rca":
                    Rm[k] = r_micro(ev_r, Rbar, p["k_rca"], p["frac_rca"] / 100.0, p["k_ph"])
                else:
                    Rm[k] = r_micro(ev_l, Rbar, p["k_lca"], p["frac_lca"] / 100.0, 1.0)
            else:
                Rm[k] = Rbar
        return E, Rm

    def edges(self, Rm, valves):
        p = self.p
        g = [("pvn", "la", 1.0 / p["R_pvn"]),
             ("la", "lv", 1.0 / valves["mv"]),
             ("lv", "ao", 1.0 / valves["av"]),
             ("ao", "sa", 1.0 / p["R_ao"]),
             ("sa", "sv", 1.0 / p["R_sa"]),
             ("sv", "ra", 1.0 / p["R_sv"]),
             ("ra", "rv", 1.0 / valves["tv"]),
             ("rv", "pr", 1.0 / valves["pv"]),
             ("pr", "pa", 1.0 / p["R_pa"]),
             ("pa", "pvn", 1.0 / p["R_pc"])]
        for k in TERR:
            g += [("ao", "a_" + k, 1.0 / p["Ra_" + k]),
                  ("a_" + k, "m_" + k, 1.0 / Rm[k]),
                  ("m_" + k, "ra", 1.0 / p["Rv_" + k])]
        return g

    def solve(self, x_old, vol_old, E, Rm, valves, dt):
        p = self.p
        n = len(NODES)
        A = np.zeros((n, n))
        b = np.zeros(n)
        for ch in ("la", "lv", "ra", "rv"):
            i = IX[ch]
            A[i, i] += 1.0 / (E[ch] * dt)
            b[i] += vol_old[ch] / dt
        for nd, C in (("sa", p["C_sa"]), ("sv", p["C_sv"]), ("pa", p["C_pa"]), ("pvn", p["C_pvn"])):
            i = IX[nd]
            A[i, i] += C / dt
            b[i] += C * x_old[i] / dt
        for k in TERR:
            ia, im = IX["a_" + k], IX["m_" + k]
            A[ia, ia] += p["Ca_" + k] / dt
            b[ia] += p["Ca_" + k] * x_old[ia] / dt
            iv = IX["rv"] if k == "rca" else IX["lv"]  # Eq. 12: RCA with P_RV, LAD and LCx with P_LV
            Cm = p["Cm_" + k]
            A[im, im] += Cm / dt
            A[im, iv] += -Cm * self.imp / dt
            b[im] += Cm * (x_old[im] - self.imp * x_old[iv]) / dt
        for u, v, g in self.edges(Rm, valves):
            i, j = IX[u], IX[v]
            A[i, i] += g
            A[i, j] -= g
            A[j, j] += g
            A[j, i] -= g
        return np.linalg.solve(A, b)


VALVES = (("mv", "la", "lv"), ("av", "lv", "ao"), ("tv", "ra", "rv"), ("pv", "rv", "pr"))


def simulate(inputs, settings):
    p = dict(inputs)
    c = Circ(p, settings)
    dt = float(settings["dt"])
    t_end = float(settings["t_end"])
    T = p["T"]
    nsteps = int(round(t_end / dt))
    x = np.full(len(NODES), float(p["P_init"]))
    E0, _ = c.params_at(0.0)
    vol = {ch: x[IX[ch]] / E0[ch] for ch in ("la", "lv", "ra", "rv")}
    state = {v: False for v, _, _ in VALVES}
    rec = []
    t_rec = t_end - 2.0 * T - 1e-9
    for i in range(nsteps):
        t1 = (i + 1) * dt
        E, Rm = c.params_at(t1)
        for _ in range(20):
            valves = {v: (p["R_open"] if state[v] else p["R_closed"]) for v, _, _ in VALVES}
            xn = c.solve(x, vol, E, Rm, valves, dt)
            new = {v: bool(xn[IX[u]] >= xn[IX[d]]) for v, u, d in VALVES}
            if new == state:
                break
            state = new
        x = xn
        vol = {ch: x[IX[ch]] / E[ch] for ch in ("la", "lv", "ra", "rv")}
        if t1 >= t_rec:
            row = {"t": t1, "x": x.copy(), "open": dict(state), "vol": dict(vol),
                   "Q": {}}
            for k in TERR:
                row["Q"]["a_" + k] = (x[IX["a_" + k]] - x[IX["m_" + k]]) / Rm[k]   # distal (intramural) arterial flow
                row["Q"]["in_" + k] = (x[IX["ao"]] - x[IX["a_" + k]]) / p["Ra_" + k]
                row["Q"]["v_" + k] = (x[IX["m_" + k]] - x[IX["ra"]]) / p["Rv_" + k]
            row["Q"]["av"] = (x[IX["lv"]] - x[IX["ao"]]) / valves["av"]
            row["Rm_rca"] = Rm["rca"]
            rec.append(row)
        if not np.all(np.isfinite(x)):
            return None
    return rec


def _cycle(rec, T, dt):
    """The last full cycle that starts at mitral valve closure (t = 0 of Eqs. 13-14)."""
    n_cyc = int(round(T / dt))
    starts = [i for i in range(1, len(rec)) if rec[i - 1]["open"]["mv"] and not rec[i]["open"]["mv"]]
    starts = [i for i in starts if i + n_cyc <= len(rec)]
    if not starts:
        return None
    i0 = starts[-1]
    cyc = rec[i0:i0 + n_cyc]
    # aortic valve closure: first open -> closed transition after it opened in this cycle
    opened = False
    i_es = None
    for j, r in enumerate(cyc):
        if r["open"]["av"]:
            opened = True
        elif opened:
            i_es = j
            break
    return cyc, i_es


def _stats(q, i_es, dt, dsfr):
    qs, qd = q[:i_es], q[i_es:]
    out = {"Qs_mean": sum(qs) / len(qs), "Qd_mean": sum(qd) / len(qd),
           "Qs_peak": max(qs), "Qd_peak": max(qd), "Q_mean": sum(q) / len(q)}
    out["pDSFR"] = out["Qd_peak"] / out["Qs_peak"]                       # Eq. 13
    if dsfr == "mean":
        out["mDSFR"] = out["Qd_mean"] / out["Qs_mean"]
    else:
        out["mDSFR"] = (sum(qd) * dt) / (sum(qs) * dt)                   # Eq. 14 as printed
    return out


SERIES = {"lad": "a_lad", "lcx": "a_lcx", "rca": "a_rca", "gcv": "v_lad"}
STATS = ("Qs_mean", "Qd_mean", "Qs_peak", "Qd_peak", "Q_mean", "pDSFR", "mDSFR")
GLOBAL = ("CO", "Pao_max", "Pao_min", "Pao_mean", "Ppa_max", "Ppa_min", "Ppa_mean", "SV", "EF",
          "sys_frac", "sys_dia_ratio", "cor_frac", "left_frac", "periodicity")


def output_names():
    return [f"{s}_{v}" for v in SERIES for s in STATS] + list(GLOBAL)


def run(inputs, settings):
    nan = float("nan")
    dt = float(settings["dt"])
    T = inputs["T"]
    rec = simulate(inputs, settings)
    res = _cycle(rec, T, dt) if rec else None
    if res is None or res[1] is None:
        return {k: nan for k in output_names()}
    cyc, i_es = res
    dsfr = settings.get("dsfr", "integral")
    out = {}
    for v, key in SERIES.items():
        st = _stats([r["Q"][key] for r in cyc], i_es, dt, dsfr)
        for s in STATS:
            out[f"{s}_{v}"] = st[s]
    pao = [r["x"][IX["ao"]] for r in cyc]
    ppa = [r["x"][IX["pr"]] for r in cyc]
    vlv = [r["vol"]["lv"] for r in cyc]
    qav = [r["Q"]["av"] for r in cyc]
    qcor = [sum(r["Q"]["in_" + k] for k in TERR) for r in cyc]
    qleft = [r["Q"]["in_lad"] + r["Q"]["in_lcx"] for r in cyc]
    co = sum(qav) / len(qav)
    out.update({
        "CO": co * 60.0 / 1000.0,
        "Pao_max": max(pao), "Pao_min": min(pao), "Pao_mean": sum(pao) / len(pao),
        "Ppa_max": max(ppa), "Ppa_min": min(ppa), "Ppa_mean": sum(ppa) / len(ppa),
        "SV": max(vlv) - min(vlv), "EF": 100.0 * (max(vlv) - min(vlv)) / max(vlv),
        "sys_frac": 100.0 * i_es / len(cyc),
        "sys_dia_ratio": 100.0 * i_es / (len(cyc) - i_es),
        "cor_frac": 100.0 * sum(qcor) / sum(qav),
        "left_frac": 100.0 * sum(qleft) / sum(qcor),
    })
    # change of mean aortic pressure over the last cycle relative to the one before (steadiness check)
    n_cyc = int(round(T / dt))
    allp = [r["x"][IX["ao"]] for r in rec]
    prev = allp[-2 * n_cyc:-n_cyc]
    last = allp[-n_cyc:]
    out["periodicity"] = 100.0 * abs(sum(last) - sum(prev)) / abs(sum(last))
    return out
