# Ursino 1998, Eqs. 1-42: pulsatile heart and circulation (Eqs. 1-29) under carotid
# baroreflex control (Eqs. 30-42), integrated with fixed-step classical Runge-Kutta.
# Ports are in the units declared in model.yaml: mmHg, ml, s, spikes/s.
# The pure delays (Eqs. 35, 38, 40) read the stored efferent frequencies at t - D,
# held over one step. Mean values are time averages (trapezoidal) over the whole
# heart periods completed in the last `t_average` seconds, as the paper describes.
import math

_STATE = ["Ppa", "Fpa", "Ppp", "Ppv", "Psa", "Fsa", "Psp", "Pev", "Pla", "Vlv",
          "Pra", "Vrv", "xi", "y", "dEl", "dEr", "dRsp", "dRep", "dVsv", "dVev",
          "dTs", "dTv"]


def _simulate(p, s, fixed_T):
    dt = float(s["dt"])
    t_settle = float(s["t_settle"])
    t_avg = float(s["t_average"])
    n_total = int(round((t_settle + t_avg) / dt))
    n_start_avg = int(round(t_settle / dt))

    # Unstressed volumes not under control (Eq. 10)
    Vu_fixed = (p["Vu_sa"] + p["Vu_sp"] + p["Vu_ep"] + p["Vu_ra"] + p["Vu_pa"]
                + p["Vu_pp"] + p["Vu_pv"] + p["Vu_la"])
    tz_tp = p["tau_z"] / p["tau_p"]

    def afferent(P):  # Eq. 31
        e = math.exp((P - p["Pn"]) / p["ka"])
        return (p["fmin"] + p["fmax"] * e) / (1.0 + e)

    def f_es(fcs):  # Eq. 33
        return p["fes_inf"] + (p["fes0"] - p["fes_inf"]) * math.exp(-p["kes"] * fcs)

    def f_ev(fcs):  # Eq. 34
        e = math.exp((fcs - p["fcs0"]) / p["kev"])
        return (p["fev0"] + p["fev_inf"] * e) / (1.0 + e)

    def sigma(G, fes):  # Eqs. 35, 38
        if fes >= p["fes_min"]:
            return G * math.log(fes - p["fes_min"] + 1.0)
        return 0.0

    # Initial state: a rough guess near the basal state; only the settled state is used.
    x = {"Ppa": 15.0, "Fpa": 90.0, "Ppp": 12.0, "Ppv": 6.0, "Psa": 90.0, "Fsa": 90.0,
         "Psp": 80.0, "Pev": 4.0, "Pla": 6.0, "Vlv": 120.0, "Pra": 3.0, "Vrv": 140.0,
         "xi": 0.0, "y": 0.0, "dEl": 0.0, "dEr": 0.0, "dRsp": 0.0, "dRep": 0.0,
         "dVsv": 0.0, "dVev": 0.0, "dTs": 0.0, "dTv": 0.0}
    # basal effector levels at the static operating point P = Pn, to start near equilibrium
    fcs_n = afferent(p["Pn"])
    fes_n = f_es(fcs_n)
    x["dEl"] = sigma(p["G_Emax_lv"], fes_n)
    x["dEr"] = sigma(p["G_Emax_rv"], fes_n)
    x["dRsp"] = sigma(p["G_R_sp"], fes_n)
    x["dRep"] = sigma(p["G_R_ep"], fes_n)
    x["dVsv"] = sigma(p["G_Vu_sv"], fes_n)
    x["dVev"] = sigma(p["G_Vu_ev"], fes_n)
    x["dTs"] = sigma(p["G_T_s"], fes_n)
    x["dTv"] = p["G_T_v"] * f_ev(fcs_n)
    x["y"] = p["Pn"] * (1.0 - tz_tp)  # P~ = Pn with Pcs = Pn
    X = [x[k] for k in _STATE]

    # delay buffers of the efferent frequencies, filled with the initial values
    hist_len = int(round(max(p["D_Emax_lv"], p["D_Emax_rv"], p["D_R_sp"], p["D_R_ep"],
                             p["D_Vu_sv"], p["D_Vu_ev"], p["D_T_s"], p["D_T_v"]) / dt)) + 2
    fes_hist = [fes_n] * hist_len
    fev_hist = [f_ev(fcs_n)] * hist_len

    def lag(D):
        return int(round(D / dt))

    lags = {k: lag(p["D_" + k]) for k in ["Emax_lv", "Emax_rv", "R_sp", "R_ep", "Vu_sv",
                                          "Vu_ev", "T_s", "T_v"]}

    def rhs(X, delayed):
        (Ppa, Fpa, Ppp, Ppv, Psa, Fsa, Psp, Pev, Pla, Vlv, Pra, Vrv, xi, y,
         dEl, dEr, dRsp, dRep, dVsv, dVev, dTs, dTv) = X
        Emax_lv = dEl + p["Emax_lv0"]           # Eq. 37
        Emax_rv = dEr + p["Emax_rv0"]
        Rsp = dRsp + p["R_sp0"]
        Rep = dRep + p["R_ep0"]
        Vusv = dVsv + p["Vu_sv0"]
        Vuev = dVev + p["Vu_ev0"]
        T = fixed_T if fixed_T is not None else dTs + dTv + p["T0"]   # Eq. 42
        Tsys = p["Tsys0"] - p["ksys"] / T        # Eq. 22
        u = xi - math.floor(xi)                  # Eq. 21
        if u <= Tsys / T:                        # Eq. 19
            phi = math.sin(math.pi * T * u / Tsys) ** 2
        else:
            phi = 0.0
        # Eqs. 18, 29
        Pmax_lv = phi * Emax_lv * (Vlv - p["Vu_lv"]) + (1.0 - phi) * p["P0_lv"] * (math.exp(p["kE_lv"] * Vlv) - 1.0)
        Pmax_rv = phi * Emax_rv * (Vrv - p["Vu_rv"]) + (1.0 - phi) * p["P0_rv"] * (math.exp(p["kE_rv"] * Vrv) - 1.0)
        # Eqs. 15-17, 26-28
        if Pmax_lv > Psa:
            Rlv = p["kR_lv"] * Pmax_lv
            Fol = (Pmax_lv - Psa) / Rlv
        else:
            Rlv = p["kR_lv"] * Pmax_lv
            Fol = 0.0
        Plv = Pmax_lv - Rlv * Fol
        if Pmax_rv > Ppa:
            Rrv = p["kR_rv"] * Pmax_rv
            For = (Pmax_rv - Ppa) / Rrv
        else:
            Rrv = p["kR_rv"] * Pmax_rv
            For = 0.0
        Prv = Pmax_rv - Rrv * For
        # Eqs. 13, 24
        Fil = (Pla - Plv) / p["R_la"] if Pla > Plv else 0.0
        Fir = (Pra - Prv) / p["R_ra"] if Pra > Prv else 0.0
        # Eqs. 9, 10
        Vu = Vu_fixed + Vusv + Vuev
        Psv = (p["Vt"] - p["C_sa"] * Psa - (p["C_sp"] + p["C_ep"]) * Psp - p["C_ev"] * Pev
               - p["C_ra"] * Pra - Vrv - p["C_pa"] * Ppa - p["C_pp"] * Ppp - p["C_pv"] * Ppv
               - p["C_la"] * Pla - Vlv - Vu) / p["C_sv"]
        # baroreflex: Eqs. 30, 36, 39, 41
        Pcs = Psa if p["Pcs_open"] is None else p["Pcs_open"]
        Pt = y + tz_tp * Pcs
        fe_d = delayed
        d = [0.0] * 22
        d[0] = (For - Fpa) / p["C_pa"]                                   # Eq. 1
        d[1] = (Ppa - Ppp - p["R_pa"] * Fpa) / p["L_pa"]                 # Eq. 2
        d[2] = (Fpa - (Ppp - Ppv) / p["R_pp"]) / p["C_pp"]               # Eq. 3
        d[3] = ((Ppp - Ppv) / p["R_pp"] - (Ppv - Pla) / p["R_pv"]) / p["C_pv"]  # Eq. 4
        d[4] = (Fol - Fsa) / p["C_sa"]                                   # Eq. 5
        d[5] = (Psa - Psp - p["R_sa"] * Fsa) / p["L_sa"]                 # Eq. 6
        d[6] = (Fsa - (Psp - Psv) / Rsp - (Psp - Pev) / Rep) / (p["C_sp"] + p["C_ep"])  # Eq. 7
        d[19] = (-dVev + sigma(p["G_Vu_ev"], fe_d["Vu_ev"])) / p["tau_Vu_ev"]
        d[7] = ((Psp - Pev) / Rep - (Pev - Pra) / p["R_ev"] - d[19]) / p["C_ev"]  # Eq. 8
        d[8] = ((Ppv - Pla) / p["R_pv"] - Fil) / p["C_la"]                # Eq. 12
        d[9] = Fil - Fol                                                  # Eq. 14
        d[10] = ((Psv - Pra) / p["R_sv"] + (Pev - Pra) / p["R_ev"] - Fir) / p["C_ra"]  # Eq. 23
        d[11] = Fir - For                                                 # Eq. 25
        d[12] = 1.0 / T                                                   # Eq. 21
        d[13] = (Pcs - Pt) / p["tau_p"]                                   # Eq. 30 (y = P~ - tz/tp Pcs)
        d[14] = (-dEl + sigma(p["G_Emax_lv"], fe_d["Emax_lv"])) / p["tau_Emax_lv"]
        d[15] = (-dEr + sigma(p["G_Emax_rv"], fe_d["Emax_rv"])) / p["tau_Emax_rv"]
        d[16] = (-dRsp + sigma(p["G_R_sp"], fe_d["R_sp"])) / p["tau_R_sp"]
        d[17] = (-dRep + sigma(p["G_R_ep"], fe_d["R_ep"])) / p["tau_R_ep"]
        d[18] = (-dVsv + sigma(p["G_Vu_sv"], fe_d["Vu_sv"])) / p["tau_Vu_sv"]
        d[20] = (-dTs + sigma(p["G_T_s"], fe_d["T_s"])) / p["tau_T_s"]
        d[21] = (-dTv + p["G_T_v"] * fe_d["T_v_ev"]) / p["tau_T_v"]
        aux = (Fol, (Psp - Psv) / Rsp, Emax_lv, Emax_rv, Rsp, Rep, Vusv, Vuev, T, Psa,
               Pt, Fsa, Psv, Plv)
        return d, aux

    nx = len(X)
    # record cycle boundaries during the averaging window
    cyc_marks = []
    acc_series = []
    xi_before = 0.0
    for n in range(n_total):
        Pt_now = X[13] + tz_tp * (X[4] if p["Pcs_open"] is None else p["Pcs_open"])
        e = math.exp((Pt_now - p["Pn"]) / p["ka"])
        fcs = (p["fmin"] + p["fmax"] * e) / (1.0 + e)
        fes_hist.append(f_es(fcs))
        fev_hist.append(f_ev(fcs))
        L = len(fes_hist)
        delayed = {k: fes_hist[L - 1 - lags[k]] for k in lags if k != "T_v"}
        delayed["T_v_ev"] = fev_hist[L - 1 - lags["T_v"]]
        if L > 4 * hist_len:
            del fes_hist[: L - hist_len]
            del fev_hist[: L - hist_len]
        k1, aux = rhs(X, delayed)
        if n >= n_start_avg:
            acc_series.append(aux)
            xi_before = X[12]
        X2 = [X[i] + 0.5 * dt * k1[i] for i in range(nx)]
        k2, _ = rhs(X2, delayed)
        X3 = [X[i] + 0.5 * dt * k2[i] for i in range(nx)]
        k3, _ = rhs(X3, delayed)
        X4 = [X[i] + dt * k3[i] for i in range(nx)]
        k4, _ = rhs(X4, delayed)
        X = [X[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(nx)]
        if n >= n_start_avg and math.floor(X[12]) > math.floor(xi_before):
            cyc_marks.append(len(acc_series))  # index of the first sample of the next cycle
        if any(v != v for v in X):
            raise FloatingPointError("integration diverged")
    # average over whole cycles: samples from the first to the last cycle start
    if len(cyc_marks) < 2:
        i0, i1 = 0, len(acc_series) - 1
    else:
        i0, i1 = cyc_marks[0], cyc_marks[-1]
    seg = acc_series[i0:i1 + 1]
    m = len(seg[0])
    means = []
    for j in range(m):
        tot = 0.0
        for a, b in zip(seg[:-1], seg[1:]):
            tot += 0.5 * (a[j] + b[j])
        means.append(tot / (len(seg) - 1))
    names = ["CO", "Fsp", "Emax_lv", "Emax_rv", "Rsp", "Rep", "Vusv", "Vuev", "T", "Psa",
             "Pt", "Fsa", "Psv", "Plv"]
    return dict(zip(names, means))


def _params(inputs):
    p = dict(inputs)
    p["Pcs_open"] = None
    return p


def simulate(inputs, settings, fixed_T=None):
    """Mean values over the settled state; fixed_T (s) cuts the heart-period loop (pacing)."""
    return _simulate(_params(inputs), settings, fixed_T)


def run(inputs, settings):
    m = simulate(inputs, settings)
    return {
        "CO": m["CO"],
        "F_sp": m["Fsp"],
        "sp_fraction": 100.0 * m["Fsp"] / m["CO"],
        "SAP": m["Psa"],
        "T": m["T"],
        "Emax_lv": m["Emax_lv"],
        "Emax_rv": m["Emax_rv"],
        "R_sp": m["Rsp"],
        "R_ep": m["Rep"],
        "Vu_sv": m["Vusv"],
        "Vu_ev": m["Vuev"],
    }
