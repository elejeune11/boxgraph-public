# The circulation of circulation_ch2 (Eqs. 2-1 to 2-23 as printed), evaluated at an instant t of
# the simulation, so that the waveforms the chapter plots (Figs. 2-9 to 2-20) can be compared with
# figure readings point by point. The integration is circulation_ch2's own (its `simulate`, RK4 at
# dt); this file only asks it to record every state over the plotted window. The setting `signed`
# runs the corrected variant of Eq. 2-13 (circulation_ch2_signed). One simulation per set of inputs
# and settings is kept in memory, so a sweep over t costs one simulation.
import importlib.util
import math
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_ch2", os.path.join(_here, "..", "circulation_ch2", "model.py"))
_cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cv)

_MEMO = {}

# order of the recorded sample (circulation_ch2.simulate with extra=True)
_COLS = ("t", "Plv", "Pla", "Prv", "Pra", "Psas", "Ppas", "Qao", "Qmi", "Qpo", "Qti",
         "Vlv", "Vla", "Vrv", "Vra", "l", "l_r", "th_ao", "th_mi", "th_po", "th_ti",
         "elv", "erv", "ela", "era")
NAMES = ("Plv", "Pla", "Prv", "Pra", "Psas", "Ppas", "Qao", "Qmi", "Qpo", "Qti",
         "Vlv", "Vla", "Vrv", "Vra", "l", "th_ao", "th_mi", "th_po", "th_ti", "elv", "ela")
_DEG = 180.0 / math.pi


def _simulate(p, settings):
    rec = _cv.simulate(p, settings, signed=bool(settings.get("signed", False)),
                       window=(float(settings["t_from"]), float(settings["t_to"])), extra=True)
    return rec, float(settings["dt"])


def run(inputs, settings):
    base = {k: v for k, v in inputs.items() if k != "t"}
    key = (tuple(sorted(base.items())), tuple(sorted((k, str(v)) for k, v in settings.items())))
    if key not in _MEMO:
        _MEMO.clear()
        _MEMO[key] = _simulate(base, settings)
    rec, dt = _MEMO[key]
    nan = float("nan")
    if not rec:
        return {k: nan for k in NAMES}
    t = float(inputs["t"])
    j = (t - rec[0][0]) / dt
    i = int(math.floor(j))
    if i < 0 or i + 1 >= len(rec):
        return {k: nan for k in NAMES}
    w = j - i
    row = {c: (1 - w) * a + w * b for c, a, b in zip(_COLS, rec[i], rec[i + 1])}
    out = {k: row[k] for k in NAMES}
    for k in ("th_ao", "th_mi", "th_po", "th_ti"):
        if settings.get("valve_dynamics"):
            out[k] = row[k] * _DEG
        else:
            # on-off valves (Eq. 2-14): the plotted angle is theta_max when the valve is open (AR = 1)
            # and theta_min when it is shut; open where the flow through it is positive
            q = {"th_ao": row["Qao"], "th_mi": row["Qmi"], "th_po": row["Qpo"], "th_ti": row["Qti"]}[k]
            v = k[3:]
            out[k] = inputs[f"theta_max_{v}"] if q > 0 else inputs[f"theta_min_{v}"]
    return out
