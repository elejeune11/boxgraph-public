# Closed-loop minimal CVS model of Smith et al. 2004 (Fig. 1, Eqs. 1-20 and the
# "open on pressure, close on flow" valve law of Sec. 2.4.2), as the paper states it.
# Units: pressure mmHg, volume ml, time s, flow ml/s.
import math

# initial distribution of the stressed volume among the six chambers, in the order
# lv, ao, vc, rv, pa, pu (a setting: the paper says only that the initial volumes are
# "approximated based on normal heart function")
_ORDER = ("lv", "ao", "vc", "rv", "pa", "pu")


def _drive(t, period, A, B, C):
    tau = t % period
    return A * math.exp(-B * (tau - C) ** 2)


def _vspt(e, Vlv, Vrv, p, guess):
    """Solve Eq. 20 for the septum volume by Newton's method with a bracketing fallback."""
    def f(v):
        xs = p["lam_spt"] * (v - p["V0_spt"])
        xl = p["lam_lvf"] * (Vlv - v - p["V0_lvf"])
        xr = p["lam_rvf"] * (Vrv + v - p["V0_rvf"])
        el, er, es = math.exp(xl), math.exp(xr), math.exp(xs)
        val = (e * p["E_spt"] * (v - p["Vd_spt"]) + (1 - e) * p["P0_spt"] * (es - 1)
               - e * p["E_lvf"] * (Vlv - v - p["Vd_lvf"]) - (1 - e) * p["P0_lvf"] * (el - 1)
               + e * p["E_rvf"] * (Vrv + v - p["Vd_rvf"]) + (1 - e) * p["P0_rvf"] * (er - 1))
        der = (e * p["E_spt"] + (1 - e) * p["P0_spt"] * p["lam_spt"] * es
               + e * p["E_lvf"] + (1 - e) * p["P0_lvf"] * p["lam_lvf"] * el
               + e * p["E_rvf"] + (1 - e) * p["P0_rvf"] * p["lam_rvf"] * er)
        return val, der
    v = guess
    for _ in range(50):
        val, der = f(v)
        step = val / der
        v -= step
        if abs(step) < 1e-10:
            return v
    # fallback: bisection on a wide bracket (f is increasing in v)
    lo, hi = -Vrv - 50.0, Vlv + 50.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid)[0] > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def _pressures(t, Vlv, Vrv, p, vs_guess):
    e = _drive(t, p["period"], p["A"], p["B"], p["C"])
    Vpcd = Vlv + Vrv                                                      # Eq. 11
    Ppcd = p["P0_pcd"] * (math.exp(p["lam_pcd"] * (Vpcd - p["V0_pcd"])) - 1)  # Eq. 18
    Pperi = Ppcd + p["P_th"]                                              # Eq. 14
    Vspt = _vspt(e, Vlv, Vrv, p, vs_guess)                                # Eq. 20
    Vlvf = Vlv - Vspt                                                     # Eq. 9
    Vrvf = Vrv + Vspt                                                     # Eq. 10
    Plvf = (e * p["E_lvf"] * (Vlvf - p["Vd_lvf"])
            + (1 - e) * p["P0_lvf"] * (math.exp(p["lam_lvf"] * (Vlvf - p["V0_lvf"])) - 1))  # Eq. 16
    Prvf = (e * p["E_rvf"] * (Vrvf - p["Vd_rvf"])
            + (1 - e) * p["P0_rvf"] * (math.exp(p["lam_rvf"] * (Vrvf - p["V0_rvf"])) - 1))
    return Plvf + Pperi, Prvf + Pperi, Vspt                               # Eqs. 12, 13


def _rhs(t, y, p, cache):
    Vlv, Vao, Vvc, Vrv, Vpa, Vpu, Qav, Qpv = y
    Plv, Prv, Vspt = _pressures(t, Vlv, Vrv, p, cache["vspt"])
    cache["vspt"] = Vspt
    pul_shift = p["P_th"] * p["pth_pulm"]
    Pao = p["E_ao"] * (Vao - p["Vd_ao"])                                  # Eq. 1, linear chambers
    Pvc = p["E_vc"] * (Vvc - p["Vd_vc"])
    Ppa = p["E_pa"] * (Vpa - p["Vd_pa"]) + pul_shift
    Ppu = p["E_pu"] * (Vpu - p["Vd_pu"]) + pul_shift
    # inlet valves, no inertia (Eq. 6), closed when the flow would be negative
    Qmt = max(0.0, (Ppu - Plv) / p["R_mt"])
    Qtc = max(0.0, (Pvc - Prv) / p["R_tc"])
    # outlet valves with inertia (Eq. 7), open on pressure, close on flow
    qav, qpv = max(Qav, 0.0), max(Qpv, 0.0)
    dQav = 0.0 if (Qav <= 0.0 and Plv - Pao <= 0.0) else (Plv - Pao - qav * p["R_av"]) / p["L_av"]
    dQpv = 0.0 if (Qpv <= 0.0 and Prv - Ppa <= 0.0) else (Prv - Ppa - qpv * p["R_pv"]) / p["L_pv"]
    Qsys = (Pao - Pvc) / p["R_sys"]                                       # Eq. 6
    Qpul = (Ppa - Ppu) / p["R_pul"]
    dy = (Qmt - qav, qav - Qsys, Qsys - Qtc, Qtc - qpv, qpv - Qpul, Qpul - Qmt, dQav, dQpv)  # Eq. 8
    return dy, (Plv, Prv, Pao, Pvc, Ppa, Ppu, Vspt)


def simulate(p, settings):
    dt = float(settings["dt"])
    n_beats = int(settings["n_beats"])
    frac = settings["initial_fractions"]
    total = sum(frac[k] for k in _ORDER)
    y = [p["V_tot"] * frac[k] / total for k in _ORDER] + [0.0, 0.0]
    period = p["period"]
    n_per = int(round(period / dt))
    cache = {"vspt": 2.0}
    last = []
    t = 0.0
    for beat in range(n_beats):
        record = beat == n_beats - 1
        for i in range(n_per):
            t = (beat * n_per + i) * dt
            k1, aux = _rhs(t, y, p, cache)
            if record:
                last.append((y[0], y[3], aux))
            y2 = [a + 0.5 * dt * b for a, b in zip(y, k1)]
            k2, _ = _rhs(t + 0.5 * dt, y2, p, cache)
            y3 = [a + 0.5 * dt * b for a, b in zip(y, k2)]
            k3, _ = _rhs(t + 0.5 * dt, y3, p, cache)
            y4 = [a + dt * b for a, b in zip(y, k3)]
            k4, _ = _rhs(t + dt, y4, p, cache)
            y = [a + dt / 6.0 * (b1 + 2 * b2 + 2 * b3 + b4) for a, b1, b2, b3, b4 in zip(y, k1, k2, k3, k4)]
            # valve closes when its flow becomes negative (close on flow)
            if y[6] < 0.0:
                y[6] = 0.0
            if y[7] < 0.0:
                y[7] = 0.0
    return last


def _params(inputs):
    p = dict(inputs)
    p["period"] = 60.0 / inputs["HR"]
    return p


def summarize(last, HR):
    Vlv = [r[0] for r in last]
    Vrv = [r[1] for r in last]
    Pao = [r[2][2] for r in last]
    Ppa = [r[2][4] for r in last]
    Pvc = [r[2][3] for r in last]
    Ppu = [r[2][5] for r in last]
    Vspt = [r[2][6] for r in last]
    sv = max(Vlv) - min(Vlv)
    return {
        "SV_lv": sv,
        "SV_rv": max(Vrv) - min(Vrv),
        "CO": sv * HR / 1000.0,
        "Pao_sys": max(Pao),
        "Pao_dia": min(Pao),
        "Ppa_sys": max(Ppa),
        "Ppa_dia": min(Ppa),
        "Pvc_mean": sum(Pvc) / len(Pvc),
        "Ppu_mean": sum(Ppu) / len(Ppu),
        "Vspt_swing": max(Vspt) - min(Vspt),
    }


def run(inputs, settings):
    p = _params(inputs)
    return summarize(simulate(p, settings), inputs["HR"])
