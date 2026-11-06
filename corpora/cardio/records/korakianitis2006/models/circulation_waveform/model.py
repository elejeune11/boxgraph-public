# The circulation model of circulation_valves (Eqs. 1-20, as printed), evaluated at an instant t
# of the simulation, so that the waveforms the paper plots (Figs. 4-13) can be compared with
# figure readings point by point. The integration is circulation_valves' own (_Sys, _params,
# RK4 at DT with the angle limits applied after each step); this file only records every state
# and the valve-leaflet force terms of Eq. 14 over the plotted window. One simulation per set of
# inputs is kept in memory, so a sweep over t costs one simulation.
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_valves", os.path.join(_here, "..", "circulation_valves", "model.py"))
_cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cv)

_MEMO = {}

NAMES = ("Plv", "Pla", "Psas", "Prv", "Pra", "Ppas", "Qmi", "Qao", "Qti", "Qpo",
         "Vlv", "Vla", "Vrv", "Vra", "th_ao", "th_mi", "th_po", "th_ti",
         "acc_p_mi", "acc_f_mi", "acc_b_mi", "acc_v_mi")


def _simulate(inputs, settings):
    p = _cv._params(inputs)
    s = _cv._Sys(p, settings)
    dt = float(settings["dt"])
    t_end = float(settings["t_end"])
    t_rec = float(settings["t_record"])
    y = [0.0] * len(_cv.STATE)
    y[0], y[1], y[2], y[3] = inputs["Vla_init"], inputs["Vlv_init"], inputs["Vra_init"], inputs["Vrv_init"]
    y[4], y[6], y[8] = inputs["Psas_init"], inputs["Psat_init"], inputs["Psvn_init"]
    y[9], y[11], y[13] = inputs["Ppas_init"], inputs["Ppat_init"], inputs["Ppvn_init"]
    for k, v in ((14, "ao"), (16, "mi"), (18, "po"), (20, "ti")):
        y[k] = p["thmin_" + v]
    n = int(round(t_end / dt))
    i0 = int(round(t_rec / dt))
    rec = []
    for i in range(n + 1):
        t = i * dt
        if i >= i0:
            Plv, Pla, Prv, Pra, dps, Q = s.aux(t, y)
            th, w = y[16], y[17]
            # Eq. 14 terms for the mitral leaflet, as the model integrates them
            ap = dps["mi"] * p["Kp_mi"] * math.cos(th)
            af = -p["Kf_mi"] * w
            ab = p["Kb_mi"] * Q["mi"] * math.cos(th)
            av = -p["Kv_mi"] * Q["mi"] * math.sin(s.vf * th) if Q["mi"] >= 0 else 0.0
            if s.dynamic:
                angles = [y[14] / _cv.DEG, y[16] / _cv.DEG, y[18] / _cv.DEG, y[20] / _cv.DEG]
            else:
                angles = [float("nan")] * 4
            rec.append((Plv, Pla, y[4], Prv, Pra, y[9], Q["mi"], Q["ao"], Q["ti"], Q["po"],
                        y[1], y[0], y[3], y[2], *angles, ap, af, ab, av))
        if i == n:
            break
        k1 = s.rhs(t, y)
        y2 = [a + 0.5 * dt * b for a, b in zip(y, k1)]
        k2 = s.rhs(t + 0.5 * dt, y2)
        y3 = [a + 0.5 * dt * b for a, b in zip(y, k2)]
        k3 = s.rhs(t + 0.5 * dt, y3)
        y4 = [a + dt * b for a, b in zip(y, k3)]
        k4 = s.rhs(t + dt, y4)
        y = [a + dt / 6.0 * (b + 2 * c + 2 * e + f) for a, b, c, e, f in zip(y, k1, k2, k3, k4)]
        y = s.clamp(y)
        if any(math.isnan(v) for v in y):
            break
    return t_rec, dt, rec


def run(inputs, settings):
    base = {k: v for k, v in inputs.items() if k != "t"}
    key = (tuple(sorted(base.items())), tuple(sorted((k, str(v)) for k, v in settings.items())))
    if key not in _MEMO:
        _MEMO.clear()
        _MEMO[key] = _simulate(base, settings)
    t_rec, dt, rec = _MEMO[key]
    t = float(inputs["t"])
    j = (t - t_rec) / dt
    i = int(math.floor(j))
    nan = float("nan")
    if i < 0 or i + 1 >= len(rec):
        return {k: nan for k in NAMES}
    w = j - i
    return {k: (1 - w) * a + w * b for k, a, b in zip(NAMES, rec[i], rec[i + 1])}
