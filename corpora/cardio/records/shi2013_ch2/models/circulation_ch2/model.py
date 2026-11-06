# Closed-loop circulation of thesis Chapter 2 (Eqs. 2-1 to 2-23), as printed.
# Heart: four variable-elastance chambers (Eqs. 2-1 to 2-6), KG diaphragm motion (Eqs. 2-7 to
# 2-12), four valves with the orifice law (Eq. 2-13) and either on-off opening (Eq. 2-14) or
# leaflet dynamics (Eqs. 2-15, 2-17). Systemic and pulmonary loops (Eqs. 2-18 to 2-23).
# Port units: mmHg, ml, ml/s, s; angles in degrees; KG coefficients as in Table 2-3 (SI).
# Settings switch the three features on or off, as the chapter's five configurations do.
# No I/O. Fixed-step RK4 (the chapter's "4-stage Runge-Kutta method"); statistics over one period.
import math

PI = math.pi
DEG = PI / 180.0
PA_PER_MMHG = 133.322387415
ML_PER_M3 = 1.0e6


def _act_v(tc, Ts1, Ts2):
    # Eq. 2-3
    if tc < Ts1:
        return 1.0 - math.cos(tc / Ts1 * PI)
    if tc < Ts2:
        return 1.0 + math.cos((tc - Ts1) / (Ts2 - Ts1) * PI)
    return 0.0


def _act_a(tc, T, Tpb, Tpw):
    # Eq. 2-6
    if tc < Tpb + Tpw - T:
        return 1.0 - math.cos((tc - Tpb + T) / Tpw * 2.0 * PI)
    if tc < Tpb:
        return 0.0
    return 1.0 - math.cos((tc - Tpb) / Tpw * 2.0 * PI)


def simulate(p, settings, signed=False, window=None, extra=False):
    """Integrate; return the samples of the analysed period. `signed` puts a minus sign on the
    reverse branch of Eq. 2-13 (used only by the corrected variant). `window` (t0, t1) records
    the samples from t0 to t1 instead, with absolute times; `extra` appends the four leaflet
    angles (rad) and the four chamber elastances to each sample (used by the waveform model)."""
    dt = float(settings["dt"])
    t_end = float(settings["t_end"])
    t0w = float(settings["t_window"])
    ac = bool(settings["atrial_contraction"])
    kg = bool(settings["kg_motion"])
    vd = bool(settings["valve_dynamics"])
    per_mass = settings.get("kg_form", "eq2_10") == "per_mass"

    T, Ts1, Ts2, Tpb, Tpw = p["T"], p["Ts1"], p["Ts2"], p["Tpwb"], p["Tpww"]
    Elvs, Elvd, Ervs, Ervd = p["Elvs"], p["Elvd"], p["Ervs"], p["Ervd"]
    Elamax, Elamin, Eramax, Eramin = p["Ela_max"], p["Ela_min"], p["Era_max"], p["Era_min"]
    Plv0, Vlv0, Pla0, Vla0 = p["Plv0"], p["Vlv0"], p["Pla0"], p["Vla0"]
    Prv0, Vrv0, Pra0, Vra0 = p["Prv0"], p["Vrv0"], p["Pra0"], p["Vra0"]
    CQao, CQmi, CQpo, CQti = p["CQao"], p["CQmi"], p["CQpo"], p["CQti"]
    Csas, Rsas, Lsas, Csat, Rsat, Lsat = p["Csas"], p["Rsas"], p["Lsas"], p["Csat"], p["Rsat"], p["Lsat"]
    Rs_tot = p["Rsat"] + p["Rsar"] + p["Rscp"]
    Rsvn, Csvn = p["Rsvn"], p["Csvn"]
    Cpas, Rpas, Lpas, Cpat, Lpat = p["Cpas"], p["Rpas"], p["Lpas"], p["Cpat"], p["Lpat"]
    Rp_tot = p["Rpat"] + p["Rpar"] + p["Rpcp"]
    Rpvn, Cpvn = p["Rpvn"], p["Cpvn"]
    Kp = (p["Kp_ao"], p["Kp_mi"], p["Kp_po"], p["Kp_ti"])
    Kf = (p["Kf_ao"], p["Kf_mi"], p["Kf_po"], p["Kf_ti"])
    thmax = (p["theta_max_ao"] * DEG, p["theta_max_mi"] * DEG, p["theta_max_po"] * DEG, p["theta_max_ti"] * DEG)
    thmin = (p["theta_min_ao"] * DEG, p["theta_min_mi"] * DEG, p["theta_min_po"] * DEG, p["theta_min_ti"] * DEG)
    den = tuple((1.0 - math.cos(h)) ** 2 for h in thmax)
    CQ = (CQao, CQmi, CQpo, CQti)
    # KG diaphragm (Eq. 2-10). The tissue-force term K_st * e is taken numerically, with e in
    # mmHg/ml, as Table 2-3's units (m/(s^2 mmHg)) leave a per-ml factor unaccounted (q_kg_units).
    # eq2_10: M l'' = K_st,a e_a - K_st,v e_v + dP A - K_f l' - K_e l, Table 2-3 values as printed;
    # per_mass: l'' = K_st,a e_a - K_st,v e_v + dP A / m - K_f l' - K_e l (Table 2-3 units: 1/s, 1/s^2).
    kL = (p["Kst_la"], p["Kst_lv"], p["Kf_sav"], p["Ke_sav"], p["m_sav"], p["A_sav"])
    kR = (p["Kst_ra"], p["Kst_rv"], p["Kf_pav"], p["Ke_pav"], p["m_pav"], p["A_pav"])

    def kg_acc(kc, ea, ev, dP_mmHg, l, v):
        Ka, Kv, Kfr, Ke, m, A = kc
        f = Ka * ea - Kv * ev + dP_mmHg * PA_PER_MMHG * A / (m if per_mass else 1.0) - Kfr * v - Ke * l
        return f if per_mass else f / m

    def aux(t, y):
        tc = t % T
        ev = _act_v(tc, Ts1, Ts2)
        elv = Elvd + (Elvs - Elvd) / 2.0 * ev                       # Eq. 2-2
        erv = Ervd + (Ervs - Ervd) / 2.0 * ev
        if ac:
            ea = _act_a(tc, T, Tpb, Tpw)
            ela = Elamin + (Elamax - Elamin) / 2.0 * ea              # Eq. 2-5
            era = Eramin + (Eramax - Eramin) / 2.0 * ea
        else:
            ela, era = Elamin, Eramin                                # constant E_la,min
        if kg:
            dVL = kL[5] * y[22] * ML_PER_M3                          # Eqs. 2-11, 2-12
            dVR = kR[5] * y[24] * ML_PER_M3
        else:
            dVL = dVR = 0.0
        Vlv, Vla = y[1] + dVL, y[0] - dVL
        Vrv, Vra = y[3] + dVR, y[2] - dVR
        Plv = Plv0 + elv * (Vlv - Vlv0)                              # Eq. 2-4
        Pla = Pla0 + ela * (Vla - Vla0)
        Prv = Prv0 + erv * (Vrv - Vrv0)
        Pra = Pra0 + era * (Vra - Vra0)
        dps = (Plv - y[4], Pla - Plv, Prv - y[9], Pra - Prv)
        Q = [0.0, 0.0, 0.0, 0.0]
        for i in range(4):
            dP = dps[i]
            if vd:
                th = y[14 + 2 * i]
                th = thmin[i] if th < thmin[i] else (thmax[i] if th > thmax[i] else th)
                ar = (1.0 - math.cos(th)) ** 2 / den[i]              # Eq. 2-15
            else:
                ar = 1.0 if dP >= 0 else 0.0                         # Eq. 2-14
            q = CQ[i] * ar * math.sqrt(abs(dP))                      # Eq. 2-13 as printed
            if signed and dP < 0:
                q = -q
            Q[i] = q
        return elv, erv, ela, era, Plv, Pla, Prv, Pra, Vlv, Vla, Vrv, Vra, dps, Q

    def rhs(t, y):
        elv, erv, ela, era, Plv, Pla, Prv, Pra, Vlv, Vla, Vrv, Vra, dps, Q = aux(t, y)
        Qsvn = (y[8] - Pra) / Rsvn                                   # Eq. 2-23
        Qpvn = (y[13] - Pla) / Rpvn
        d = [0.0] * 26
        d[0] = Qpvn - Q[1]
        d[1] = Q[1] - Q[0]                                           # Eq. 2-1
        d[2] = Qsvn - Q[3]
        d[3] = Q[3] - Q[2]
        d[4] = (Q[0] - y[5]) / Csas                                  # Eq. 2-18
        d[5] = (y[4] - y[6] - Rsas * y[5]) / Lsas                    # Eq. 2-19
        d[6] = (y[5] - y[7]) / Csat                                  # Eq. 2-20
        d[7] = (y[6] - y[8] - Rs_tot * y[7]) / Lsat                  # Eq. 2-21
        d[8] = (y[7] - Qsvn) / Csvn                                  # Eq. 2-22
        d[9] = (Q[2] - y[10]) / Cpas
        d[10] = (y[9] - y[11] - Rpas * y[10]) / Lpas
        d[11] = (y[10] - y[12]) / Cpat
        d[12] = (y[11] - y[13] - Rp_tot * y[12]) / Lpat
        d[13] = (y[12] - Qpvn) / Cpvn
        if vd:
            for i in range(4):
                k = 14 + 2 * i
                d[k] = y[k + 1]
                d[k + 1] = Kp[i] * dps[i] * math.cos(y[k]) - Kf[i] * y[k + 1]   # Eq. 2-17
        if kg:
            d[22] = y[23]
            d[23] = kg_acc(kL, ela, elv, Plv - Pla, y[22], y[23])
            d[24] = y[25]
            d[25] = kg_acc(kR, era, erv, Prv - Pra, y[24], y[25])
        return d

    y = [0.0] * 26
    y[0], y[1], y[2], y[3] = p["Vla_init"], p["Vlv_init"], p["Vra_init"], p["Vrv_init"]
    y[4], y[6], y[8] = p["Psas_init"], p["Psat_init"], p["Psvn_init"]
    y[9], y[11], y[13] = p["Ppas_init"], p["Ppat_init"], p["Ppvn_init"]
    for i in range(4):
        y[14 + 2 * i] = thmin[i]
    n = int(round(t_end / dt))
    i_start = int(round(t0w / dt))
    i_stop = int(round((t0w + T) / dt))
    t_off = t0w
    if window is not None:
        i_start = int(round(window[0] / dt))
        i_stop = int(round(window[1] / dt)) + 1
        n = max(n, i_stop)
        t_off = 0.0
    rec = []
    h2 = 0.5 * dt
    h6 = dt / 6.0
    for it in range(n):
        t = it * dt
        if i_start <= it < i_stop:
            a = aux(t, y)
            Q = a[13]
            row = (t - t_off, a[4], a[5], a[6], a[7], y[4], y[9], Q[0], Q[1], Q[2], Q[3],
                   a[8], a[9], a[10], a[11], y[22], y[24])
            if extra:
                row = row + (y[14], y[16], y[18], y[20], a[0], a[1], a[2], a[3])
            rec.append(row)
        k1 = rhs(t, y)
        k2 = rhs(t + h2, [a + h2 * b for a, b in zip(y, k1)])
        k3 = rhs(t + h2, [a + h2 * b for a, b in zip(y, k2)])
        k4 = rhs(t + dt, [a + dt * b for a, b in zip(y, k3)])
        y = [a + h6 * (b + 2.0 * c + 2.0 * e + f) for a, b, c, e, f in zip(y, k1, k2, k3, k4)]
        if vd:
            for i in range(4):
                k = 14 + 2 * i
                if y[k] <= thmin[i]:
                    y[k] = thmin[i]
                    if y[k + 1] < 0:
                        y[k + 1] = 0.0
                elif y[k] >= thmax[i]:
                    y[k] = thmax[i]
                    if y[k + 1] > 0:
                        y[k + 1] = 0.0
        if not all(math.isfinite(v) and abs(v) < 1e12 for v in y):
            return None
    return rec


KEYS = ("Plv_max", "Plv_min", "Psas_max", "Psas_min", "Prv_max", "Ppas_max", "Pla_max", "Pra_max",
        "CO", "Vlv_max", "Vlv_min", "SV", "Vla_max", "Vla_min", "Vrv_max", "Vrv_min",
        "Vlv_pwb", "Vla_pwb", "Vrv_pwb", "Vra_pwb", "Vla_trough", "Vra_trough",
        "Qao_max", "Qmi_max", "Qpo_max", "Qti_max", "Qmi_E", "Qmi_A", "EA_mi", "Qti_E", "Qti_A", "EA_ti",
        "l_min", "l_max")


def summarise(rec, p):
    nan = float("nan")
    if not rec or any(not math.isfinite(v) for r in rec for v in r):
        return {k: nan for k in KEYS}
    tc, Plv, Pla, Prv, Pra, Psas, Ppas, Qao, Qmi, Qpo, Qti, Vlv, Vla, Vrv, Vra, lL, lR = zip(*rec)
    T, Ts2, Tpb, Tpw = p["T"], p["Ts2"], p["Tpwb"], p["Tpww"]
    wrap = Tpb + Tpw - T
    e_idx = [i for i, t in enumerate(tc) if Ts2 <= t < Tpb]          # E wave: after systole, before the P wave
    a_idx = [i for i, t in enumerate(tc) if t >= Tpb or t < wrap]   # A wave: during atrial activation
    tr_idx = [i for i, t in enumerate(tc) if t >= Tpb or t < 0.1]   # atrial trough: activation and just after
    i_pwb = min(range(len(tc)), key=lambda i: abs(tc[i] - Tpb))
    qmiE = max(Qmi[i] for i in e_idx)
    qmiA = max(Qmi[i] for i in a_idx)
    qtiE = max(Qti[i] for i in e_idx)
    qtiA = max(Qti[i] for i in a_idx)
    return {
        "Plv_max": max(Plv), "Plv_min": min(Plv), "Psas_max": max(Psas), "Psas_min": min(Psas),
        "Prv_max": max(Prv), "Ppas_max": max(Ppas), "Pla_max": max(Pla), "Pra_max": max(Pra),
        "CO": sum(Qao) / len(Qao) * 60.0 / 1000.0,
        "Vlv_max": max(Vlv), "Vlv_min": min(Vlv), "SV": max(Vlv) - min(Vlv),
        "Vla_max": max(Vla), "Vla_min": min(Vla), "Vrv_max": max(Vrv), "Vrv_min": min(Vrv),
        "Vlv_pwb": Vlv[i_pwb], "Vla_pwb": Vla[i_pwb], "Vrv_pwb": Vrv[i_pwb], "Vra_pwb": Vra[i_pwb],
        "Vla_trough": min(Vla[i] for i in tr_idx), "Vra_trough": min(Vra[i] for i in tr_idx),
        "Qao_max": max(Qao), "Qmi_max": max(Qmi), "Qpo_max": max(Qpo), "Qti_max": max(Qti),
        "Qmi_E": qmiE, "Qmi_A": qmiA, "EA_mi": qmiE / qmiA if qmiA > 0 else nan,
        "Qti_E": qtiE, "Qti_A": qtiA, "EA_ti": qtiE / qtiA if qtiA > 0 else nan,
        "l_min": min(lL), "l_max": max(lL),
    }


def run(inputs, settings):
    return summarise(simulate(inputs, settings), inputs)
