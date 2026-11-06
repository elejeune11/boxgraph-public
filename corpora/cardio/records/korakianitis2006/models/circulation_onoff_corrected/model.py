# The simplified (on-off valve, Eq. 7) configuration of circulation_valves_corrected, as one model.
# A helper for the relation to korakianitis_cellml/closed_loop_onoff: the CellML documentation says
# the original model's "heart valve dynamics, have been simplified", which is this paper's Section 3.1
# simplified model ("on-off heart valve model as described by Eq. (7)"). A relation runs a model with
# its own settings, so the on-off configuration needs a model of its own.
# The integration and statistics are circulation_valves_corrected's own; with on-off valves the leaflet
# inputs (Table 3, Table 4) are not used, so they are not ports here and are passed as placeholders.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_circulation_valves_corrected", os.path.join(_here, "..", "circulation_valves_corrected", "model.py"))
_cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cv)

_UNUSED = {}
for _v in ("ao", "mi", "po", "ti"):
    for _k in ("Kp_", "Kf_", "Kb_", "Kv_"):
        _UNUSED[_k + _v] = 0.0
    _UNUSED["theta_max_" + _v] = 75.0
    _UNUSED["theta_min_" + _v] = 0.0
_UNUSED["theta_ref_mi"] = 75.0


def run(inputs, settings):
    full = dict(_UNUSED)
    full.update(inputs)
    s = dict(settings)
    s["valve_model"] = "on_off"
    return _cv.run(full, s)
