"""Python port of the CellML model ModelMain (four heart chambers with variable elastance and
on-off valves, a five-segment systemic loop and a five-segment pulmonary loop, closed).

Our own code: a translation of the CellML equations (files and lines in model.yaml comments).
Pressures in mmHg (the code's UnitP), volumes in mL (UnitV), flows in mL/s, time in s.
The integration scheme is ours (the CellML files hold no solver settings): classical RK4
at a fixed step `dt`, from t = 0 to `t_end`; results are taken over the last heart period.
"""

import math


def _floor_mod(t, T):
    # mt = t - T*floor(t/T)   (EAtrium / EVentricle)
    return t - T * math.floor(t / T)


def _e_atrium(t, Emax, Emin, p):
    # EAtrium.cellml line 22 (et), line 24 (E)
    T, Tpwb, Tpww, pi = p["T"], p["Tpwb"], p["Tpww"], p["pi"]
    mt = _floor_mod(t, T)
    if 0 <= mt <= (Tpwb + Tpww) * T - T:
        et = 1 - math.cos(2 * pi * ((mt - Tpwb * T) + T) / (Tpww * T))
    elif (Tpwb + Tpww) * T - T < mt <= Tpwb * T:
        et = 0.0
    elif Tpwb * T < mt <= T:
        et = 1 - math.cos(2 * pi * (mt - Tpwb * T) / (Tpww * T))
    else:  # not reached: mt is in [0, T)
        et = 0.0
    return Emin + et * (Emax - Emin) / 2


def _e_ventricle(t, Emax, Emin, p):
    # EVentricle.cellml line 20
    T, Ts1, Ts2, pi = p["T"], p["Ts1"], p["Ts2"], p["pi"]
    mt = _floor_mod(t, T)
    if 0 <= mt <= Ts1 * T:
        et = 1 - math.cos(pi * mt / (Ts1 * T))
    elif Ts1 * T < mt <= Ts2 * T:
        et = 1 + math.cos(pi * (mt - Ts1 * T) / ((Ts2 - Ts1) * T))
    else:  # Ts2*T < mt < T
        et = 0.0
    return Emin + et * (Emax - Emin) / 2


def _valve(CV, Pi, Po):
    # TempCDa / TempCDv: Tao = 1 if Pi >= Po else 0;
    # Qo = CV*Tao*|Pi-Po|^0.5 (Pi >= Po), -1*CV*Tao*|Po-Pi|^0.5 (Pi < Po)
    if Pi >= Po:
        return CV * 1.0 * abs(Pi - Po) ** 0.5
    return -1 * CV * 0.0 * abs(Po - Pi) ** 0.5


def _algebra(t, y, p):
    (Vla, Vlv, Vra, Vrv, Psas, Qsas, Psat, Qsat, Psvn,
     Ppas, Qpas, Ppat, Qpat, Ppvn) = y
    Ela = _e_atrium(t, p["ElaMax"], p["ElaMin"], p)
    Elv = _e_ventricle(t, p["ElvMax"], p["ElvMin"], p)
    Era = _e_atrium(t, p["EraMax"], p["EraMin"], p)
    Erv = _e_ventricle(t, p["ErvMax"], p["ErvMin"], p)
    # chambers (TempCDa, TempCDv): Pi = Pini + E*(V - Vini)
    Pla = p["PlaIni"] + Ela * (Vla - p["VlaIni"])
    Plv = p["PlvIni"] + Elv * (Vlv - p["VlvIni"])
    Pra = p["PraIni"] + Era * (Vra - p["VraIni"])
    Prv = p["PrvIni"] + Erv * (Vrv - p["VrvIni"])
    # valves: the outflow of each chamber (ModelHeart: LA.Po = LV.Pi, RA.Po = RV.Pi;
    # LV.Po = LeftHeart.Po = SysLoop.Pi = Sas.Pi; RV.Po = RightHeart.Po = PulLoop.Pi = Pas.Pi)
    Qmi = _valve(p["CVmi"], Pla, Plv)
    Qao = _valve(p["CVao"], Plv, Psas)
    Qti = _valve(p["CVti"], Pra, Prv)
    Qpo = _valve(p["CVpa"], Prv, Ppas)
    # systemic arteriole and capillary (TempR): Pi = Po + R*Qi, Qo = Qi, carrying Qsat
    Pscp = Psvn + p["Rscp"] * Qsat          # Scp.Pi; Scp.Po = Svn.Pi
    Psar = Pscp + p["Rsar"] * Qsat          # Sar.Pi = Sat.Po
    # systemic vein (TempRC): Qo = (Pi - Po)/R; Po = SysLoop.Po = RightHeart.Pi = RA.Pi
    Qsvn = (Psvn - Pra) / p["Rsvn"]
    # pulmonary arteriole and capillary, carrying Qpat
    Ppcp = Ppvn + p["Rpcp"] * Qpat
    Ppar = Ppcp + p["Rpar"] * Qpat          # Par.Pi = Pat.Po
    # pulmonary vein: Po = PulLoop.Po = LeftHeart.Pi = LA.Pi
    Qpvn = (Ppvn - Pla) / p["Rpvn"]
    return dict(Pla=Pla, Plv=Plv, Pra=Pra, Prv=Prv, Qmi=Qmi, Qao=Qao, Qti=Qti, Qpo=Qpo,
                Psar=Psar, Qsvn=Qsvn, Ppar=Ppar, Qpvn=Qpvn)


def _rhs(t, y, p):
    (Vla, Vlv, Vra, Vrv, Psas, Qsas, Psat, Qsat, Psvn,
     Ppas, Qpas, Ppat, Qpat, Ppvn) = y
    a = _algebra(t, y, p)
    return (
        a["Qpvn"] - a["Qmi"],                                   # LA: dV/dt = Qi - Qo, Qi = Pvn.Qo
        a["Qmi"] - a["Qao"],                                    # LV
        a["Qsvn"] - a["Qti"],                                   # RA: Qi = Svn.Qo
        a["Qti"] - a["Qpo"],                                    # RV
        (a["Qao"] - Qsas) / p["Csas"],                          # Sas (TempRLC): dPi/dt = (Qi - Qo)/C
        (Psas - Psat - p["Rsas"] * Qsas) / p["Lsas"],          # Sas: dQo/dt = (Pi - Po - R*Qo)/L, Po = Sat.Pi
        (Qsas - Qsat) / p["Csat"],                              # Sat
        (Psat - a["Psar"] - p["Rsat"] * Qsat) / p["Lsat"],     # Sat: Po = Sar.Pi
        (Qsat - a["Qsvn"]) / p["Csvn"],                         # Svn (TempRC): Qi = Scp.Qo = Qsat
        (a["Qpo"] - Qpas) / p["Cpas"],                          # Pas
        (Ppas - Ppat - p["Rpas"] * Qpas) / p["Lpas"],          # Pas: Po = Pat.Pi
        (Qpas - Qpat) / p["Cpat"],                              # Pat
        (Ppat - a["Ppar"] - p["Rpat"] * Qpat) / p["Lpat"],     # Pat: Po = Par.Pi
        (Qpat - a["Qpvn"]) / p["Cpvn"],                         # Pvn: Qi = Pcp.Qo = Qpat
    )


def simulate(p, dt, t_end):
    # initial values: V = V0 (TempCD), Pi = P0 and Qo = Q0 (TempRLC), Pi = P0 (TempRC)
    y = (p["Vla0"], p["Vlv0"], p["Vra0"], p["Vrv0"],
         p["P0sas"], p["Q0sas"], p["P0sat"], p["Q0sat"], p["P0svn"],
         p["P0pas"], p["Q0pas"], p["P0pat"], p["Q0pat"], p["P0pvn"])
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
    t_end = float(settings.get("t_end", 11.0))
    rows = simulate(p, dt, t_end)
    T = p["T"]
    t0 = t_end - T
    Plv, Prv, Psas, Ppas, Vlv, Qao = [], [], [], [], [], []
    Qmi_E, Qti_E = [], []
    for t, y in rows:
        if t < t0 - 1e-12:
            continue
        a = _algebra(t, y, p)
        Plv.append(a["Plv"])
        Prv.append(a["Prv"])
        Psas.append(y[4])
        Ppas.append(y[9])
        Vlv.append(y[1])
        Qao.append(a["Qao"])
        # E peak: largest atrioventricular flow between the end of ventricular activation
        # (Ts2*T) and the start of atrial activation (Tpwb*T) in the analysed cycle
        mt = t - t0
        if p["Ts2"] * T < mt <= p["Tpwb"] * T:
            Qmi_E.append(a["Qmi"])
            Qti_E.append(a["Qti"])

    def mean(xs):  # trapezoidal mean over one period on the uniform grid
        return sum((u + v) / 2 for u, v in zip(xs[:-1], xs[1:])) * dt / T

    return {
        "P_lv_max": max(Plv), "P_lv_min": min(Plv),
        "P_sas_max": max(Psas), "P_sas_min": min(Psas),
        "P_rv_max": max(Prv), "P_pas_max": max(Ppas),
        "V_lv_max": max(Vlv), "V_lv_min": min(Vlv),
        "SV": max(Vlv) - min(Vlv),
        "Q_ao_mean": mean(Qao) * 60 / 1000,   # mL/s -> L/min
        "Q_ao_peak": max(Qao),
        "Q_mi_E": max(Qmi_E), "Q_ti_E": max(Qti_E),
    }
