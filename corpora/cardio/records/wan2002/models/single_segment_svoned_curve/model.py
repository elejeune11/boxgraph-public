# The single segment of Fig. 1 run with the released svOneDSolver (model single_segment_svoned),
# returning the inlet and outlet flow and pressure of the last computed cycle at time t of the cycle,
# for a sweep over the time axis of Fig. 1.
import importlib.util
from pathlib import Path

_d = Path(__file__).resolve().parent.parent / "single_segment_svoned"
_spec = importlib.util.spec_from_file_location("wan2002_single_segment", _d / "model.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def run(inputs, settings):
    c = base.simulate({k: v for k, v in inputs.items() if k != "t"}, settings)
    t = inputs["t"]
    if not (0.0 <= t <= c["T"] + 1e-12):
        nan = float("nan")
        return {"Q_in": nan, "Q_out": nan, "p_in": nan, "p_out": nan}
    return {k: base.oned.at_phase(c[k], c["dt"], t) for k in ("Q_in", "Q_out", "p_in", "p_out")}
