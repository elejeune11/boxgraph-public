# Pressure-volume loop features of the closed-loop model (closed_loop: Fig. 1, Eqs. 1-20,
# valve law of Sec. 2.4.2, as the paper states it) for the tests of Figs. 8-11: R_sys
# scaled by rsys_factor, the end-systolic elastances of the free walls (and, when
# ees_septum = 1, of the septum) scaled by ees_factor. The integration is closed_loop's own;
# this file only scales the inputs and summarises the last beat.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("_closed_loop", os.path.join(_here, "..", "closed_loop", "model.py"))
_cl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cl)


def run(inputs, settings):
    base = {k: v for k, v in inputs.items() if k not in ("rsys_factor", "ees_factor", "ees_septum")}
    base["R_sys"] = inputs["R_sys"] * inputs["rsys_factor"]
    base["E_lvf"] = inputs["E_lvf"] * inputs["ees_factor"]
    base["E_rvf"] = inputs["E_rvf"] * inputs["ees_factor"]
    if inputs["ees_septum"] >= 0.5:
        base["E_spt"] = inputs["E_spt"] * inputs["ees_factor"]
    last = _cl.simulate(_cl._params(base), settings)
    Vlv = [r[0] for r in last]
    Vrv = [r[1] for r in last]
    Plv = [r[2][0] for r in last]
    Prv = [r[2][1] for r in last]
    Pao = [r[2][2] for r in last]
    return {"EDV_lv": max(Vlv), "ESV_lv": min(Vlv), "Plv_max": max(Plv),
            "EDV_rv": max(Vrv), "ESV_rv": min(Vrv), "Prv_max": max(Prv),
            "Pao_sys": max(Pao), "Pao_dia": min(Pao)}
