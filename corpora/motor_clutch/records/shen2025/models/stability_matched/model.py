# Phase boundaries of Fig. 2(c,d), "matched substrate" ks = nc0 kc (p. 8): stability_boundaries with k~s set,
# at each Nc, to nc0 k~c at the stable fixed point (Eqs. 9-15). Everything else is the printed model's code
# (A3 as printed), loaded from it.
import importlib.util
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "stability_boundaries" / "model.py"
_spec = importlib.util.spec_from_file_location("shen2025_stability_boundaries_m", _SRC)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    p = dict(inputs)
    p["ks"] = 0.0
    _, nc0, _ = _base._fixed(p)
    p["ks"] = nc0 * p["kc"]
    return _base.run(p, settings)
