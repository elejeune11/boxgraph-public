# Corrected variant of circulation_valves (Eqs. 1-20). Everything is as printed except the
# corrections listed in model.yaml, each marked "CORRECTED" below:
#   Eq. 3  ventricular activation 1 - cos / 1 + cos (EVentricle.cellml line 20, Fig. 2)
#   Eq. 6  minus sign on the reverse-flow branch (TempCDv.cellml line 48)
#   Eq. 14 vortex term K_v Q sin(2 theta), as in Eq. 13 and the 45 deg text (setting vortex_angle_factor)
#   Eq. 18 artery flow driven by P_sat - P_svn (TempRLC.cellml line 25 with ModelSys.cellml lines 69-79),
#          and likewise P_pat - P_pvn in the pulmonary loop
# Port units: mmHg, ml, ml/s, s, degrees for angles. No I/O. Fixed-step RK4; statistics over one period.
import math

PI = math.pi
DEG = PI / 180.0

STATE = ("Vla", "Vlv", "Vra", "Vrv",
         "Psas", "Qsas", "Psat", "Qsat", "Psvn",
         "Ppas", "Qpas", "Ppat", "Qpat", "Ppvn",
         "th_ao", "w_ao", "th_mi", "w_mi", "th_po", "w_po", "th_ti", "w_ti")


def _e_ventricle(tc, Ts1, Ts2):
    # CORRECTED Eq. 3: e(t) rises from 0 to 2 at T_s1 and falls back to 0 at T_s2
    if tc <= Ts1:
        return 1.0 - math.cos(tc / Ts1 * PI)
    if tc <= Ts2:
        return 1.0 + math.cos((tc - Ts1) / (Ts2 - Ts1) * PI)
    return 0.0


def _e_atrium(tc, Tpb, Tpw):
    # Eq. 5 as printed
    if Tpb <= tc < Tpb + Tpw:
        return 1.0 - math.cos((tc - Tpb) / Tpw * 2.0 * PI)
    return 0.0


def _valve_flow(CQ, AR, dP):
    # CORRECTED Eq. 6: Q = -CQ AR sqrt(P_down - P_up) when the pressure difference is negative
    q = CQ * AR * math.sqrt(abs(dP))
    return q if dP >= 0 else -q


def _area(th, th_ref):
    # Eq. 8
    return (1.0 - math.cos(th)) ** 2 / (1.0 - math.cos(th_ref)) ** 2


class _Sys:
    def __init__(self, p, settings):
        self.p = p
        self.dynamic = settings.get("valve_model", "dynamic") == "dynamic"
        self.vf = float(settings.get("vortex_angle_factor", 2))

    def aux(self, t, y):
        p = self.p
        tc = t % p["T"]
        ev = _e_ventricle(tc, p["Ts1"], p["Ts2"])
        ea = _e_atrium(tc, p["Tpwb"], p["Tpww"])
        elv = p["Elvd"] + (p["Elvs"] - p["Elvd"]) / 2.0 * ev          # Eq. 2
        erv = p["Ervd"] + (p["Ervs"] - p["Ervd"]) / 2.0 * ev
        ela = p["Ela_min"] + (p["Ela_max"] - p["Ela_min"]) / 2.0 * ea
        era = p["Era_min"] + (p["Era_max"] - p["Era_min"]) / 2.0 * ea
        Plv = p["Plv0"] + elv * (y[1] - p["Vlv0"])                     # Eq. 4
        Pla = p["Pla0"] + ela * (y[0] - p["Vla0"])
        Prv = p["Prv0"] + erv * (y[3] - p["Vrv0"])
        Pra = p["Pra0"] + era * (y[2] - p["Vra0"])
        dps = {"ao": Plv - y[4], "mi": Pla - Plv, "po": Prv - y[9], "ti": Pra - Prv}
        th = {"ao": y[14], "mi": y[16], "po": y[18], "ti": y[20]}
        Q = {}
        for v in ("ao", "mi", "po", "ti"):
            if self.dynamic:
                lo, hi = p["thmin_" + v], p["thmax_" + v]
                ar = _area(min(max(th[v], lo), hi), p["thref_" + v])
            else:
                ar = 1.0 if dps[v] >= 0 else 0.0                         # Eq. 7
            Q[v] = _valve_flow(p["CQ" + v], ar, dps[v])
        return Plv, Pla, Prv, Pra, dps, Q

    def rhs(self, t, y):
        p = self.p
        Plv, Pla, Prv, Pra, dps, Q = self.aux(t, y)
        Qsvn = (y[8] - Pra) / p["Rsvn"]                                  # Eq. 20
        Qpvn = (y[13] - Pla) / p["Rpvn"]
        d = [0.0] * len(STATE)
        d[0] = Qpvn - Q["mi"]
        d[1] = Q["mi"] - Q["ao"]                                         # Eq. 1
        d[2] = Qsvn - Q["ti"]
        d[3] = Q["ti"] - Q["po"]
        d[4] = (Q["ao"] - y[5]) / p["Csas"]                              # Eq. 15
        d[5] = (y[4] - y[6] - p["Rsas"] * y[5]) / p["Lsas"]              # Eq. 16
        d[6] = (y[5] - y[7]) / p["Csat"]                                 # Eq. 17
        # CORRECTED Eq. 18: P_sat - P_svn drives Q_sat (printed: P_sas - P_svn)
        d[7] = (y[6] - y[8] - (p["Rsat"] + p["Rsar"] + p["Rscp"]) * y[7]) / p["Lsat"]
        d[8] = (y[7] - Qsvn) / p["Csvn"]                                 # Eq. 19
        d[9] = (Q["po"] - y[10]) / p["Cpas"]
        d[10] = (y[9] - y[11] - p["Rpas"] * y[10]) / p["Lpas"]
        d[11] = (y[10] - y[12]) / p["Cpat"]
        # CORRECTED Eq. 18, pulmonary loop ("similar"): P_pat - P_pvn drives Q_pat
        d[12] = (y[11] - y[13] - (p["Rpat"] + p["Rpar"] + p["Rpcp"]) * y[12]) / p["Lpat"]
        d[13] = (y[12] - Qpvn) / p["Cpvn"]
        if self.dynamic:
            for k, v in ((14, "ao"), (16, "mi"), (18, "po"), (20, "ti")):
                th, w = y[k], y[k + 1]
                acc = (dps[v] * p["Kp_" + v] * math.cos(th) - p["Kf_" + v] * w
                       + p["Kb_" + v] * Q[v] * math.cos(th))           # Eq. 14
                if Q[v] >= 0:
                    # CORRECTED Eq. 14 vortex term: sin(2 theta) as in Eq. 13 (vortex_angle_factor 2)
                    acc -= p["Kv_" + v] * Q[v] * math.sin(self.vf * th)
                d[k] = w
                d[k + 1] = acc
        return d

    def clamp(self, y):
        if not self.dynamic:
            return y
        p = self.p
        for k, v in ((14, "ao"), (16, "mi"), (18, "po"), (20, "ti")):
            lo, hi = p["thmin_" + v], p["thmax_" + v]
            if y[k] <= lo:
                y[k] = lo
                if y[k + 1] < 0:
                    y[k + 1] = 0.0
            elif y[k] >= hi:
                y[k] = hi
                if y[k + 1] > 0:
                    y[k + 1] = 0.0
        return y


def _params(inp):
    p = dict(inp)
    for v in ("ao", "mi", "po", "ti"):
        p["thmax_" + v] = inp["theta_max_" + v] * DEG
        p["thmin_" + v] = inp["theta_min_" + v] * DEG
        p["thref_" + v] = inp["theta_max_" + v] * DEG
    p["thref_mi"] = inp["theta_ref_mi"] * DEG
    return p


def _step(s, t, y, dt):
    k1 = s.rhs(t, y)
    y2 = [a + 0.5 * dt * b for a, b in zip(y, k1)]
    k2 = s.rhs(t + 0.5 * dt, y2)
    y3 = [a + 0.5 * dt * b for a, b in zip(y, k2)]
    k3 = s.rhs(t + 0.5 * dt, y3)
    y4 = [a + dt * b for a, b in zip(y, k3)]
    k4 = s.rhs(t + dt, y4)
    return [a + dt / 6.0 * (b + 2 * c + 2 * e + f) for a, b, c, e, f in zip(y, k1, k2, k3, k4)]


def initial_state(inputs, p):
    y = [0.0] * len(STATE)
    y[0], y[1], y[2], y[3] = inputs["Vla_init"], inputs["Vlv_init"], inputs["Vra_init"], inputs["Vrv_init"]
    y[4], y[6], y[8] = inputs["Psas_init"], inputs["Psat_init"], inputs["Psvn_init"]
    y[9], y[11], y[13] = inputs["Ppas_init"], inputs["Ppat_init"], inputs["Ppvn_init"]
    for k, v in ((14, "ao"), (16, "mi"), (18, "po"), (20, "ti")):
        y[k] = p["thmin_" + v]
    return y


def simulate(inputs, settings):
    p = _params(inputs)
    s = _Sys(p, settings)
    dt = float(settings["dt"])
    t_end = float(settings["t_end"])
    t0w = float(settings["t_window"])
    y = initial_state(inputs, p)
    n = int(round(t_end / dt))
    rec = []
    rk4 = settings.get("scheme", "rk4") == "rk4"
    for i in range(n):
        t = i * dt
        if t >= t0w - 1e-12 and t < t0w + p["T"] - 1e-12:
            Plv, Pla, Prv, Pra, dps, Q = s.aux(t, y)
            rec.append((t - t0w, Plv, Pla, Prv, Pra, y[4], y[9], Q["ao"], Q["mi"], Q["po"], Q["ti"],
                        y[1], y[0], y[3], y[2]))
        if rk4:
            y = _step(s, t, y, dt)
        else:
            k1 = s.rhs(t, y)
            y = [a + dt * b for a, b in zip(y, k1)]
        y = s.clamp(y)
        if any(math.isnan(v) for v in y):
            break
    return rec


def run(inputs, settings):
    # the same statistics of the analysed cycle as circulation_valves (q_e_peak_window)
    rec = simulate(inputs, settings)
    nan = float("nan")
    keys = ("Plv_max", "Plv_min", "Psas_max", "Psas_min", "Psas_ed", "Prv_max", "Ppas_max", "CO",
            "Vlv_max", "Vlv_min", "SV", "Qao_max", "Qpo_max", "Qmi_E", "Qti_E", "Qmi_A",
            "Qmi_dmin", "Qao_rev", "Qpo_rev", "Qmi_rev", "Qti_rev")
    if not rec or len(rec) < 10 or any(math.isnan(v) for r in rec for v in r):
        return {k: nan for k in keys}
    col = list(zip(*rec))
    tc, Plv, Pla, Prv, Pra, Psas, Ppas, Qao, Qmi, Qpo, Qti, Vlv, Vla, Vrv, Vra = col
    Tpb = inputs["Tpwb"]
    Ts2 = inputs["Ts2"]
    e_idx = [i for i, t in enumerate(tc) if Ts2 <= t < Tpb]
    a_idx = [i for i, t in enumerate(tc) if t >= Tpb]
    iE = max(e_idx, key=lambda i: Qmi[i])
    d_idx = [i for i in e_idx if i >= iE]
    return {
        "Plv_max": max(Plv), "Plv_min": min(Plv),
        "Psas_max": max(Psas), "Psas_min": min(Psas), "Psas_ed": Psas[0],
        "Prv_max": max(Prv), "Ppas_max": max(Ppas),
        "CO": sum(Qao) / len(Qao) * 60.0 / 1000.0,
        "Vlv_max": max(Vlv), "Vlv_min": min(Vlv), "SV": max(Vlv) - min(Vlv),
        "Qao_max": max(Qao), "Qpo_max": max(Qpo),
        "Qmi_E": Qmi[iE], "Qti_E": max(Qti[i] for i in e_idx),
        "Qmi_A": max(Qmi[i] for i in a_idx),
        "Qmi_dmin": min(Qmi[i] for i in d_idx),
        "Qao_rev": -min(Qao), "Qpo_rev": -min(Qpo), "Qmi_rev": -min(Qmi), "Qti_rev": -min(Qti),
    }
