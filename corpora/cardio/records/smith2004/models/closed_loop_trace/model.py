# The closed-loop model of closed_loop (Fig. 1, Eqs. 1-20, valve law of Sec. 2.4.2, as the
# paper states it), evaluated at an instant t of a steady beat, so that the waveforms of
# Fig. 7 can be compared with figure readings point by point. The integration is
# closed_loop's own (simulate: fixed-step RK4 over n_beats beats); this file only reads its
# last beat at time t within the beat (t modulo the period, so t = 0 is the start of a
# beat of the driver e(t), whose peak is at C), interpolating linearly between steps.
# One simulation per set of inputs is kept in memory, so a sweep over t costs one.
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_closed_loop", os.path.join(_here, "..", "closed_loop", "model.py"))
_cl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cl)

_MEMO = {}


def _beat(base, settings):
    p = _cl._params(base)
    last = _cl.simulate(p, settings)
    rows = []
    for Vlv, Vrv, aux in last:
        Plv, Prv, Pao, Pvc, Ppa, Ppu, Vspt = aux
        rows.append({"V_lv": Vlv, "V_rv": Vrv, "P_lv": Plv, "P_rv": Prv, "P_ao": Pao,
                     "P_vc": Pvc, "P_pa": Ppa, "P_pu": Ppu})
    return p["period"], float(settings["dt"]), rows


def run(inputs, settings):
    base = {k: v for k, v in inputs.items() if k != "t"}
    key = (tuple(sorted(base.items())), tuple(sorted((k, str(v)) for k, v in settings.items())))
    if key not in _MEMO:
        _MEMO.clear()
        _MEMO[key] = _beat(base, settings)
    period, dt, rows = _MEMO[key]
    tau = float(inputs["t"]) % period
    j = tau / dt
    i = int(math.floor(j)) % len(rows)
    k = (i + 1) % len(rows)
    w = j - math.floor(j)
    return {name: (1 - w) * rows[i][name] + w * rows[k][name] for name in rows[0]}
