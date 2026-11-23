# Variant of stability_boundaries with J55 = -(Gamma/gamma)(nc0 k~c + k~s), the derivative of the fifth
# component of Eq. 18 / A1 with respect to x~s. Everything else is the printed model's code, loaded from it.
import importlib.util
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "stability_boundaries" / "model.py"
_spec = importlib.util.spec_from_file_location("shen2025_stability_boundaries", _SRC)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    _base.CORRECTED = True
    try:
        return _base.run(inputs, settings)
    finally:
        _base.CORRECTED = False
