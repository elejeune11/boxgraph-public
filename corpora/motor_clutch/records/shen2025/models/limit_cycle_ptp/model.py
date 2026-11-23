# limit_cycle with the other reading of the unstated "amplitude of y~" (q_amplitude_def): the peak-to-peak
# range max - min of y~ on the limit cycle, instead of half of it. The integration is limit_cycle's code,
# loaded from it; the frequency is unchanged.
import importlib.util
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "limit_cycle" / "model.py"
_spec = importlib.util.spec_from_file_location("shen2025_limit_cycle_ptp", _SRC)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    out = _base.run(inputs, settings)
    return {"freq": out["freq"], "amp": 2.0 * out["amp"]}
