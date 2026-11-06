# Corrected variant of circulation_waveform: the waveforms of circulation_valves_corrected
# (Eqs. 3, 6, 14 and 18 corrected; see model.yaml) at an instant t, for the figure readings.
# Same recording as circulation_waveform; the integration is circulation_valves_corrected's own.
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_valves_corrected", os.path.join(_here, "..", "circulation_valves_corrected", "model.py"))
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
    y = _cv.initial_state(inputs, p)
    n = int(round(t_end / dt))
    i0 = int(round(t_rec / dt))
    rec = []
    for i in range(n + 1):
        t = i * dt
        if i >= i0:
            Plv, Pla, Prv, Pra, dps, Q = s.aux(t, y)
            th, w = y[16], y[17]
            # Eq. 14 terms for the mitral leaflet, as the model integrates them (vortex term corrected)
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
        y = s.clamp(_cv._step(s, t, y, dt))
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
