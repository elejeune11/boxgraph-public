# The two-chamber model of two_chamber (Sec. 3, Fig. 6; Eqs. 9-20 and the valve law of
# Sec. 2.4.2, as the paper states it), evaluated at an instant t of a steady beat, so that
# the septum volume curve of Fig. 6 can be compared point by point. The right-hand side is
# two_chamber's own (_rhs) and so is the scheme (fixed-step RK4, flows clamped at zero on
# closing); this file keeps the last beat's V_spt and reads it at t modulo the period
# (t = 0 is the start of a beat of the driver e(t)). One simulation per set of inputs is
# kept in memory, so a sweep over t costs one.
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_two_chamber", os.path.join(_here, "..", "two_chamber", "model.py"))
_tc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tc)

_MEMO = {}


def _beat(base, settings):
    p = dict(base)
    p["period"] = 60.0 / base["HR"]
    dt = float(settings["dt"])
    n_beats = int(settings["n_beats"])
    y = [float(settings["V_lv_initial"]), float(settings["V_rv_initial"]), 0.0, 0.0]
    n_per = int(round(p["period"] / dt))
    cache = {"vspt": 2.0}
    vs = []
    for beat in range(n_beats):
        record = beat == n_beats - 1
        for i in range(n_per):
            t = (beat * n_per + i) * dt
            k1, aux = _tc._rhs(t, y, p, cache)
            if record:
                vs.append(aux)
            y2 = [a + 0.5 * dt * b for a, b in zip(y, k1)]
            k2, _ = _tc._rhs(t + 0.5 * dt, y2, p, cache)
            y3 = [a + 0.5 * dt * b for a, b in zip(y, k2)]
            k3, _ = _tc._rhs(t + 0.5 * dt, y3, p, cache)
            y4 = [a + dt * b for a, b in zip(y, k3)]
            k4, _ = _tc._rhs(t + dt, y4, p, cache)
            y = [a + dt / 6.0 * (b1 + 2 * b2 + 2 * b3 + b4) for a, b1, b2, b3, b4 in zip(y, k1, k2, k3, k4)]
            if y[2] < 0.0:
                y[2] = 0.0
            if y[3] < 0.0:
                y[3] = 0.0
    return p["period"], dt, vs


def run(inputs, settings):
    base = {k: v for k, v in inputs.items() if k != "t"}
    key = (tuple(sorted(base.items())), tuple(sorted((k, str(v)) for k, v in settings.items())))
    if key not in _MEMO:
        _MEMO.clear()
        _MEMO[key] = _beat(base, settings)
    period, dt, vs = _MEMO[key]
    j = (float(inputs["t"]) % period) / dt
    i = int(math.floor(j)) % len(vs)
    w = j - math.floor(j)
    return {"V_spt": (1 - w) * vs[i] + w * vs[(i + 1) % len(vs)]}
