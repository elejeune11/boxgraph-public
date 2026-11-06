# Port to Python of the CellML model smith_chase_nokes_shaw_wake_2004.cellml
# (corpus/cardio/code/smith_cellml), components environment ... flow, lines 85-1410, and the
# connections of lines 1411-1624. Our code: the CellML itself is not copied or run.
# Every equation follows the file as written; the line numbers are given beside each.
# Units: the numbers of the CellML file, in the units it declares (pressure "kPa", volume mL,
# time s). Pressures come out in the same numbers as they go in.
# The CellML holds no solver settings; the port integrates with classical RK4 at a fixed
# step dt (a setting), solving the septum's algebraic equation by Newton's method.
import math

N_PIECES = 13  # driver_function, lines 114-359: tau is defined for time <= 13 * period only


def _tau(time, period, cyclic=False):
    """driver_function lines 111-360: tau = time - k*period for time <= (k+1)*period, k = 0..12.
    The piecewise has no <otherwise>: beyond 13 periods tau is undefined. cyclic=True is not the
    file: it is the remainder the file's documentation (line 27) says the if statements stand
    for, used only by the variant models of this record."""
    if cyclic:
        k = math.ceil(time / period) - 1
        return time if k <= 0 else time - period * k
    for k in range(N_PIECES):
        if time <= period * (k + 1):
            return time if k == 0 else time - period * k
    raise ValueError(f"tau is undefined for time {time} > {N_PIECES} * period in the CellML file")


def _e(time, p):
    tau = _tau(time, p["period"], p.get("_cyclic", False))
    return p["A"] * math.exp(-p["B"] * (tau - p["C"]) ** 2)  # lines 361-387


def _septum_residual(v, e, Vlv, Vrv, p):
    """septum lines 794-916, as written: it uses V_lv - V_spt and V_rv + V_spt directly,
    without the free walls' V_d and V_0."""
    es = math.exp(p["lambda_spt"] * (v - p["V_0_spt"]))
    el = math.exp(p["lambda_lvf"] * (Vlv - v))
    er = math.exp(p["lambda_rvf"] * (Vrv + v))
    f = (e * p["E_es_spt"] * (v - p["V_d_spt"]) + (p["one"] - e) * p["P_0_spt"] * (es - p["one"])
         - e * p["E_es_lvf"] * (Vlv - v) - (1 - e) * p["P_0_lvf"] * (el - 1)
         + e * p["E_es_rvf"] * (Vrv + v) + (1 - e) * p["P_0_rvf"] * (er - 1))
    df = (e * p["E_es_spt"] + (p["one"] - e) * p["P_0_spt"] * p["lambda_spt"] * es
          + e * p["E_es_lvf"] + (1 - e) * p["P_0_lvf"] * p["lambda_lvf"] * el
          + e * p["E_es_rvf"] + (1 - e) * p["P_0_rvf"] * p["lambda_rvf"] * er)
    return f, df


def _vspt(e, Vlv, Vrv, p, guess):
    v = guess
    for _ in range(60):
        f, df = _septum_residual(v, e, Vlv, Vrv, p)
        step = f / df
        v -= step
        if abs(step) < 1e-11:
            return v
    raise ArithmeticError("septum equation did not converge")


def _algebra(time, y, p, guess):
    Vlv, Vrv, Vpa, Vpu, Vao, Vvc, Qmt, Qav, Qtc, Qpv = y
    e = _e(time, p)
    Vspt = _vspt(e, Vlv, Vrv, p, guess)
    # pericardium lines 400-443
    Vpcd = Vlv + Vrv
    Ppcd = p["P_0_pcd"] * (math.exp(p["lambda_pcd"] * (Vpcd - p["V_0_pcd"])) - 1)
    Pperi = Ppcd + p["P_th"]
    # left_ventricle lines 465-504, lvf_calculator lines 570-608
    Vlvf = Vlv - Vspt
    Pes_lvf = p["E_es_lvf"] * (Vlvf - p["V_d_lvf"])
    Ped_lvf = p["P_0_lvf"] * (math.exp(p["lambda_lvf"] * (Vlvf - p["V_0_lvf"])) - 1)
    Plv = e * Pes_lvf + (1 - e) * Ped_lvf + Pperi
    # right_ventricle lines 630-669, rvf_calculator lines 735-773
    Vrvf = Vrv + Vspt
    Pes_rvf = p["E_es_rvf"] * (Vrvf - p["V_d_rvf"])
    Ped_rvf = p["P_0_rvf"] * (math.exp(p["lambda_rvf"] * (Vrvf - p["V_0_rvf"])) - 1)
    Prv = e * Pes_rvf + (1 - e) * Ped_rvf + Pperi
    # vessels: pulmonary_artery 932-948, pulmonary_vein 995-1011, aorta 1054-1066, vena_cava 1112-1124
    Ppa = p["E_es_pa"] * (Vpa - p["V_d_pa"]) + p["P_th"]
    Ppu = p["E_es_pu"] * (Vpu - p["V_d_pu"]) + p["P_th"]
    Pao = p["E_es_ao"] * (Vao - p["V_d_ao"])
    Pvc = p["E_es_vc"] * (Vvc - p["V_d_vc"])
    return dict(e=e, Vspt=Vspt, Plv=Plv, Prv=Prv, Ppa=Ppa, Ppu=Ppu, Pao=Pao, Pvc=Pvc)


def _rhs(time, y, p, cache):
    Vlv, Vrv, Vpa, Vpu, Vao, Vvc, Qmt, Qav, Qtc, Qpv = y
    a = _algebra(time, y, p, cache["vspt"])
    cache["vspt"] = a["Vspt"]
    Plv, Prv, Ppa, Ppu, Pao, Pvc = a["Plv"], a["Prv"], a["Ppa"], a["Ppu"], a["Pao"], a["Pvc"]
    # flow lines 1179-1204
    Qsys = (Pao - Pvc) / p["R_sys"]
    Qpul = (Ppa - Ppu) / p["R_pul"]
    # left_ventricle dV_lv/dt, lines 505-558
    if Qmt < 0 and Qav < 0:
        dVlv = 0.0
    elif Qmt < 0:
        dVlv = -Qav
    elif Qav < 0:
        dVlv = Qmt
    else:
        dVlv = Qmt - Qav
    # right_ventricle dV_rv/dt, lines 670-723
    if Qtc < 0 and Qpv < 0:
        dVrv = 0.0
    elif Qtc < 0:
        dVrv = -Qpv
    elif Qpv < 0:
        dVrv = Qtc
    else:
        dVrv = Qtc - Qpv
    dVpa = -Qpul if Qpv < 0 else Qpv - Qpul      # lines 949-978
    dVpu = Qpul if Qmt < 0 else Qpul - Qmt       # lines 1012-1038
    dVao = -Qsys if Qav < 0 else Qav - Qsys      # lines 1067-1096
    dVvc = Qsys if Qtc < 0 else Qsys - Qtc       # lines 1125-1151
    # valve flows, lines 1205-1408: held when the gradient is negative and the flow negative
    dQmt = 0.0 if (Ppu - Plv < 0 and Qmt < 0) else (Ppu - Plv - Qmt * p["R_mt"]) / p["L_mt"]
    dQav = 0.0 if (Plv - Pao < 0 and Qav < 0) else (Plv - Pao - Qav * p["R_av"]) / p["L_av"]
    dQtc = 0.0 if (Pvc - Prv < 0 and Qtc < 0) else (Pvc - Prv - Qtc * p["R_tc"]) / p["L_tc"]
    dQpv = 0.0 if (Prv - Ppa < 0 and Qpv < 0) else (Prv - Ppa - Qpv * p["R_pv"]) / p["L_pv"]
    return (dVlv, dVrv, dVpa, dVpu, dVao, dVvc, dQmt, dQav, dQtc, dQpv), a


STATE_INPUTS = ("V_lv_init", "V_rv_init", "V_pa_init", "V_pu_init", "V_ao_init", "V_vc_init",
                "Q_mt_init", "Q_av_init", "Q_tc_init", "Q_pv_init")


def simulate(p, settings):
    """Integrate from time 0 over n_beats periods; return samples of the last period."""
    dt = float(settings["dt"])
    n_beats = int(round(float(settings["n_beats"])))
    if n_beats > N_PIECES and not p.get("_cyclic", False):
        raise ValueError(f"the CellML driver is defined for {N_PIECES} periods only")
    period = p["period"]
    t_end = n_beats * period
    n = int(round(t_end / dt))
    n_last = int(round(period / dt))
    y = [p[k] for k in STATE_INPUTS]
    cache = {"vspt": float(settings.get("vspt_guess", 2.0))}
    samples = []
    for i in range(n):
        t = i * t_end / n
        t1 = (i + 1) * t_end / n
        h = t1 - t
        tm = t + 0.5 * h
        k1, a = _rhs(t, y, p, cache)
        if i >= n - n_last:
            samples.append((y, a))
        y2 = [u + 0.5 * h * k for u, k in zip(y, k1)]
        k2, _ = _rhs(tm, y2, p, cache)
        y3 = [u + 0.5 * h * k for u, k in zip(y, k2)]
        k3, _ = _rhs(tm, y3, p, cache)
        y4 = [u + h * k for u, k in zip(y, k3)]
        k4, _ = _rhs(t1, y4, p, cache)
        y = [u + h / 6.0 * (b1 + 2 * b2 + 2 * b3 + b4) for u, b1, b2, b3, b4 in zip(y, k1, k2, k3, k4)]
    return samples


def summarize(samples, period):
    Vlv = [s[0][0] for s in samples]
    Vrv = [s[0][1] for s in samples]
    col = lambda k: [s[1][k] for s in samples]  # noqa: E731
    Pao, Ppa, Pvc, Ppu, Vspt = col("Pao"), col("Ppa"), col("Pvc"), col("Ppu"), col("Vspt")
    sv = max(Vlv) - min(Vlv)
    return {
        "SV_lv": sv,
        "SV_rv": max(Vrv) - min(Vrv),
        "CO": sv * 60.0 / period / 1000.0,
        "Pao_sys": max(Pao),
        "Pao_dia": min(Pao),
        "Ppa_sys": max(Ppa),
        "Ppa_dia": min(Ppa),
        "Pvc_mean": sum(Pvc) / len(Pvc),
        "Ppu_mean": sum(Ppu) / len(Ppu),
        "Vspt_swing": max(Vspt) - min(Vspt),
    }


def run(inputs, settings, cyclic=False):
    p = dict(inputs)
    p["_cyclic"] = cyclic
    return summarize(simulate(p, settings), p["period"])
