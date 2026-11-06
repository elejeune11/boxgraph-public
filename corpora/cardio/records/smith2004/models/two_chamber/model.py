# Two-chamber model of Smith et al. 2004 (Sec. 3, Fig. 6): left and right ventricles
# coupled through the septum and pericardium (Eqs. 9-20), each filled from and emptying
# into a constant pressure through the valve law of Sec. 2.4.2.
# Units: pressure mmHg, volume ml, time s, flow ml/s.
import math


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
    lo, hi = -Vrv - 50.0, Vlv + 50.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid)[0] > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def _rhs(t, y, p, cache):
    Vlv, Vrv, Qav, Qpv = y
    e = _drive(t, p["period"], p["A"], p["B"], p["C"])
    Ppcd = p["P0_pcd"] * (math.exp(p["lam_pcd"] * (Vlv + Vrv - p["V0_pcd"])) - 1)  # Eqs. 11, 18
    Pperi = Ppcd + p["P_th"]                                                       # Eq. 14
    Vspt = _vspt(e, Vlv, Vrv, p, cache["vspt"])                                    # Eq. 20
    cache["vspt"] = Vspt
    Vlvf, Vrvf = Vlv - Vspt, Vrv + Vspt                                            # Eqs. 9, 10
    Plv = (e * p["E_lvf"] * (Vlvf - p["Vd_lvf"])
           + (1 - e) * p["P0_lvf"] * (math.exp(p["lam_lvf"] * (Vlvf - p["V0_lvf"])) - 1)) + Pperi
    Prv = (e * p["E_rvf"] * (Vrvf - p["Vd_rvf"])
           + (1 - e) * p["P0_rvf"] * (math.exp(p["lam_rvf"] * (Vrvf - p["V0_rvf"])) - 1)) + Pperi
    Qmt = max(0.0, (p["P_pu"] - Plv) / p["R_mt"])                                  # Eq. 6
    Qtc = max(0.0, (p["P_vc"] - Prv) / p["R_tc"])
    qav, qpv = max(Qav, 0.0), max(Qpv, 0.0)
    dQav = 0.0 if (Qav <= 0.0 and Plv - p["P_ao"] <= 0.0) else (Plv - p["P_ao"] - qav * p["R_av"]) / p["L_av"]  # Eq. 7
    dQpv = 0.0 if (Qpv <= 0.0 and Prv - p["P_pa"] <= 0.0) else (Prv - p["P_pa"] - qpv * p["R_pv"]) / p["L_pv"]
    return (Qmt - qav, Qtc - qpv, dQav, dQpv), Vspt                                # Eq. 8


def run(inputs, settings):
    p = dict(inputs)
    p["period"] = 60.0 / inputs["HR"]
    dt = float(settings["dt"])
    n_beats = int(settings["n_beats"])
    y = [float(settings["V_lv_initial"]), float(settings["V_rv_initial"]), 0.0, 0.0]
    n_per = int(round(p["period"] / dt))
    cache = {"vspt": 2.0}
    vs, vl = [], []
    for beat in range(n_beats):
        record = beat == n_beats - 1
        for i in range(n_per):
            t = (beat * n_per + i) * dt
            k1, aux = _rhs(t, y, p, cache)
            if record:
                vs.append(aux)
                vl.append(y[0])
            y2 = [a + 0.5 * dt * b for a, b in zip(y, k1)]
            k2, _ = _rhs(t + 0.5 * dt, y2, p, cache)
            y3 = [a + 0.5 * dt * b for a, b in zip(y, k2)]
            k3, _ = _rhs(t + 0.5 * dt, y3, p, cache)
            y4 = [a + dt * b for a, b in zip(y, k3)]
            k4, _ = _rhs(t + dt, y4, p, cache)
            y = [a + dt / 6.0 * (b1 + 2 * b2 + 2 * b3 + b4) for a, b1, b2, b3, b4 in zip(y, k1, k2, k3, k4)]
            if y[2] < 0.0:
                y[2] = 0.0
            if y[3] < 0.0:
                y[3] = 0.0
    swing = max(vs) - min(vs)
    return {"Vspt_swing": swing, "Vspt_swing_pct": 100.0 * swing / (sum(vl) / len(vl))}
