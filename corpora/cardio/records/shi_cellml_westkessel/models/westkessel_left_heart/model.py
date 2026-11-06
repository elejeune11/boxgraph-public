"""Python port of the CellML model MainWestkessel (left atrium and left ventricle with on-off
valves, driving a three-element Westerhof afterload Rc - (Rv, Cv) that returns to the left atrium).

Our own code: a line-by-line translation of the CellML equations (cited in model.yaml notes).
Pressures in mmHg (the code's UnitP), volumes in mL (UnitV), flows in mL/s, time in s.
The integration scheme is ours (the CellML files hold no solver settings): classical RK4
at a fixed step `dt`, from t = 0 to `t_end`; results are taken over the last heart period.

The aortic valve (TempCDv, Qo = CV*Tao*|Pi - Po|^0.5) feeds the characteristic resistance Zc
(TempR, Pi = Po + R*Qi), so the valve flow and the pressure upstream of Zc form an algebraic
loop. The CellML leaves it to the DAE solver; here it is solved exactly: with D = Plv - Pv,
Q = CV*sqrt(D - Rc*Q) gives Q^2 + CV^2*Rc*Q - CV^2*D = 0, whose non-negative root is taken when
D >= 0 (then Plv >= Zc.Pi, Tao = 1); when D < 0, Tao = 0, Q = 0 and Zc.Pi = Pv.
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


def _valve_into_resistance(CV, Rc, Pi, Pdown):
    # LV valve (TempCDv) in series with Zc (TempR: Zc.Pi = Zc.Po + R*Qi, Zc.Po = Zv.Pi = Pdown).
    # Returns (Qao, Zc.Pi) solving Qao = CV*Tao*|Pi - Zc.Pi|^0.5 together with Zc.Pi = Pdown + Rc*Qao.
    D = Pi - Pdown
    if D < 0:
        return 0.0, Pdown                     # Tao = 0: no flow, Zc.Pi = Pdown
    a = CV * CV * Rc
    Q = (-a + math.sqrt(a * a + 4 * CV * CV * D)) / 2
    return Q, Pdown + Rc * Q


def _algebra(t, y, p):
    Vla, Vlv, Pv = y
    Ela = _e_atrium(t, p)
    Elv = _e_ventricle(t, p)
    Pla = p["PlaIni"] + Ela * (Vla - p["VlaIni"])   # LA (TempCD): Pi = Pini + E*(V - Vini)
    Plv = p["PlvIni"] + Elv * (Vlv - p["VlvIni"])   # LV (TempCD)
    Qmi = _valve(p["CVmi"], Pla, Plv)               # LA.Qo, LA.Po = LV.Pi
    Qao, Pc = _valve_into_resistance(p["CVao"], p["Rc"], Plv, Pv)  # LV.Qo = Zc.Qi = Zc.Qo = Zv.Qi
    Qv = (Pv - Pla) / p["Rv"]                       # Zv (TempRC): Qo = (Pi - Po)/R, Po = LA.Pi
    return Pla, Plv, Qmi, Qao, Qv, Pc


def _rhs(t, y, p):
    _, _, Qmi, Qao, Qv, _ = _algebra(t, y, p)
    return (Qv - Qmi,               # LA: dV/dt = Qi - Qo, Qi = Vessel.Qo = Zv.Qo
            Qmi - Qao,              # LV: dV/dt = Qi - Qo
            (Qao - Qv) / p["Cv"])   # Zv (TempRC): dPi/dt = (Qi - Qo)/C


def simulate(p, dt, t_end):
    y = (p["Vla0"], p["Vlv0"], p["P0v"])  # initial values: V = V0 (TempCD), Zv.Pi = P0 (TempRC)
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
    Plv, Part, Vlv, Qao, Qmi = [], [], [], [], []
    for t, y in rows:
        if t < t0 - 1e-12:
            continue
        _, Plv_, Qmi_, Qao_, _, Pc = _algebra(t, y, p)
        Plv.append(Plv_)
        Part.append(Pc)          # Vessel.Pi = Zc.Pi: the arterial pressure at the aortic valve
        Vlv.append(y[1])
        Qao.append(Qao_)
        Qmi.append(Qmi_)

    def mean(xs):  # mean over one period: trapezoidal rule on the uniform grid
        return sum((a + b) / 2 for a, b in zip(xs[:-1], xs[1:])) * dt / p["T"]

    return {
        "P_lv_max": max(Plv), "P_lv_min": min(Plv),
        "P_art_max": max(Part), "P_art_min": min(Part),
        "V_lv_max": max(Vlv), "V_lv_min": min(Vlv),
        "SV": max(Vlv) - min(Vlv),
        "Q_ao_mean": mean(Qao) * 60 / 1000,   # mL/s -> L/min
        "Q_mi_mean": mean(Qmi) * 60 / 1000,
        "Q_ao_peak": max(Qao), "Q_mi_peak": max(Qmi),
    }
