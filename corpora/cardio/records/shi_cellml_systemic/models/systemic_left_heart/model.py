"""Python port of the CellML model MainSystemic (left atrium and left ventricle with on-off
valves, driving a five-segment systemic loop -- aortic sinus, artery, arteriole, capillary,
vein -- that returns to the left atrium; no pulmonary loop).

Our own code: a translation of the CellML equations (files and lines in model.yaml notes).
Pressures in mmHg (the code's UnitP), volumes in mL (UnitV), flows in mL/s, time in s.
The integration scheme is ours (the CellML files hold no solver settings): classical RK4
at a fixed step `dt`, from t = 0 to `t_end`; results are taken over the last heart period.
"""

import math


def _floor_mod(t, T):
    # mt = t - T*floor(t/T)   (EAtrium / EVentricle)
    return t - T * math.floor(t / T)


def _e_atrium(t, p):
    T, Tpwb, Tpww, pi = p["T"], p["Tpwb"], p["Tpww"], p["pi"]
    mt = _floor_mod(t, T)
    if 0 <= mt <= (Tpwb + Tpww - 1) * T:
        et = 1 - math.cos(2 * pi * (mt - (Tpwb - 1) * T) / (Tpww * T))
    elif (Tpwb + Tpww - 1) * T < mt <= Tpwb * T:
        et = 0.0
    elif Tpwb * T < mt <= T:
        et = 1 - math.cos(2 * pi * (mt - Tpwb * T) / (Tpww * T))
    else:  # not reached: mt is in [0, T)
        et = 0.0
    return p["ElaMin"] + et * (p["ElaMax"] - p["ElaMin"]) / 2


def _e_ventricle(t, p):
    T, Ts1, Ts2, pi = p["T"], p["Ts1"], p["Ts2"], p["pi"]
    mt = _floor_mod(t, T)
    if 0 <= mt <= Ts1 * T:
        et = 1 - math.cos(pi * mt / (Ts1 * T))
    elif Ts1 * T < mt <= Ts2 * T:
        et = 1 + math.cos(pi * (mt - Ts1 * T) / ((Ts2 - Ts1) * T))
    else:  # Ts2*T < mt < T
        et = 0.0
    return p["ElvMin"] + et * (p["ElvMax"] - p["ElvMin"]) / 2


def _valve(CV, Pi, Po):
    # TempCD: Tao = 1 if Pi >= Po else 0; Qo = CV*Tao*|Pi-Po|^0.5 (or -CV*Tao*|Po-Pi|^0.5 = 0)
    if Pi >= Po:
        return CV * 1.0 * abs(Pi - Po) ** 0.5
    return -1 * CV * 0.0 * abs(Po - Pi) ** 0.5


def _algebra(t, y, p):
    Vla, Vlv, Psas, Qsas, Psat, Qsat, Psvn = y
    Ela = _e_atrium(t, p)
    Elv = _e_ventricle(t, p)
    Pla = p["PlaIni"] + Ela * (Vla - p["VlaIni"])   # LA (TempCDa): Pi = Pini + E*(V - Vini)
    Plv = p["PlvIni"] + Elv * (Vlv - p["VlvIni"])   # LV (TempCDv)
    Qmi = _valve(p["CVmi"], Pla, Plv)               # LA.Qo; LA.Po = LV.Pi
    Qao = _valve(p["CVao"], Plv, Psas)              # LV.Qo; LV.Po = LEFTHeart.Po = Vessel.Pi = Sas.Pi
    # Sar, Scp (TempR): Pi = Po + R*Qi, Qo = Qi, in series from Sat.Po down to Svn.Pi, all carrying Qsat
    Pscp = Psvn + p["Rscp"] * Qsat                  # Scp.Pi; Scp.Po = Svn.Pi
    Psar = Pscp + p["Rsar"] * Qsat                  # Sar.Pi = Sat.Po; Sar.Po = Scp.Pi
    Qsvn = (Psvn - Pla) / p["Rsvn"]                 # Svn (TempRC): Qo = (Pi - Po)/R; Po = Vessel.Po = LA.Pi
    return Pla, Plv, Qmi, Qao, Psar, Qsvn


def _rhs(t, y, p):
    Vla, Vlv, Psas, Qsas, Psat, Qsat, Psvn = y
    _, _, Qmi, Qao, Psar, Qsvn = _algebra(t, y, p)
    return (Qsvn - Qmi,                                         # LA: dV/dt = Qi - Qo, Qi = Svn.Qo
            Qmi - Qao,                                          # LV: dV/dt = Qi - Qo
            (Qao - Qsas) / p["Csas"],                           # Sas (TempRLC): dPi/dt = (Qi - Qo)/C
            (Psas - Psat - p["Rsas"] * Qsas) / p["Lsas"],      # Sas: dQo/dt = (Pi - Po - R*Qo)/L, Po = Sat.Pi
            (Qsas - Qsat) / p["Csat"],                          # Sat (TempRLC): Qi = Sas.Qo
            (Psat - Psar - p["Rsat"] * Qsat) / p["Lsat"],      # Sat: Po = Sar.Pi
            (Qsat - Qsvn) / p["Csvn"])                          # Svn (TempRC): Qi = Scp.Qo = Qsat


def simulate(p, dt, t_end):
    # initial values: V = V0 (TempCD), Pi = P0 and Qo = Q0 (TempRLC), Pi = P0 (TempRC)
    y = (p["Vla0"], p["Vlv0"], p["P0sas"], p["Q0sas"], p["P0sat"], p["Q0sat"], p["P0svn"])
    n = int(round(t_end / dt))
    rows = []
    for i in range(n + 1):
        t = i * dt
        rows.append((t, y))
        if i == n:
            break
        k1 = _rhs(t, y, p)
        k2 = _rhs(t + dt / 2, tuple(a + dt / 2 * b for a, b in zip(y, k1)), p)
        k3 = _rhs(t + dt / 2, tuple(a + dt / 2 * b for a, b in zip(y, k2)), p)
        k4 = _rhs(t + dt, tuple(a + dt * b for a, b in zip(y, k3)), p)
        y = tuple(a + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4) for a, b1, b2, b3, b4 in zip(y, k1, k2, k3, k4))
    return rows


def run(inputs, settings):
    p = dict(inputs)
    dt = float(settings.get("dt", 1e-4))
    t_end = float(settings.get("t_end", 10.0))
    rows = simulate(p, dt, t_end)
    t0 = t_end - p["T"]
    Plv, Psas, Psat, Vlv, Qao, Qmi = [], [], [], [], [], []
    for t, y in rows:
        if t < t0 - 1e-12:
            continue
        _, Plv_, Qmi_, Qao_, _, _ = _algebra(t, y, p)
        Plv.append(Plv_)
        Psas.append(y[2])
        Psat.append(y[4])
        Vlv.append(y[1])
        Qao.append(Qao_)
        Qmi.append(Qmi_)

    # mean over one period: trapezoidal rule on the uniform grid
    def mean(xs):
        return sum((a + b) / 2 for a, b in zip(xs[:-1], xs[1:])) * dt / p["T"]

    return {
        "P_lv_max": max(Plv), "P_lv_min": min(Plv),
        "P_sas_max": max(Psas), "P_sas_min": min(Psas),
        "P_sat_max": max(Psat), "P_sat_min": min(Psat),
        "V_lv_max": max(Vlv), "V_lv_min": min(Vlv),
        "SV": max(Vlv) - min(Vlv),
        "Q_ao_mean": mean(Qao) * 60 / 1000,   # mL/s -> L/min
        "Q_mi_mean": mean(Qmi) * 60 / 1000,
        "Q_ao_peak": max(Qao), "Q_mi_peak": max(Qmi),
    }
