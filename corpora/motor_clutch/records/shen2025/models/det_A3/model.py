# Determinant of the Jacobian matrix exactly as printed in Eq. A3 (p. 14), at the stable fixed point.
# The matrix is the one coded in stability_boundaries (loaded from it, as printed: corrected=False).
import importlib.util
from pathlib import Path

import numpy as np

_SRC = Path(__file__).resolve().parent.parent / "stability_boundaries" / "model.py"
_spec = importlib.util.spec_from_file_location("shen2025_stability_boundaries_det", _SRC)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    return {"det": float(np.linalg.det(_base.jacobian(inputs, inputs["vu"], False)))}
