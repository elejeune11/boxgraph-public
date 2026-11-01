# The clutch model of clutch_talin_sim with talin unfolding switched off (the paper's "without talin
# unfolding" predictions, Fig. 3d,e blue lines and the dashed lines of Fig. 6a-i). It calls that model's
# simulate() with unfolding=False: clutches bind and unbind (catch bond) and transmit force, the integrin
# density stays at its basal value. Our code.
import importlib.util
from pathlib import Path

_P = Path(__file__).resolve().parent.parent / "clutch_talin_sim" / "model.py"
_spec = importlib.util.spec_from_file_location("elosegui2016_clutch_talin_sim", _P)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    out = _base.simulate(dict(inputs), settings, unfolding=False)
    return {"traction": out["traction"], "actin_flow": out["actin_flow"]}
