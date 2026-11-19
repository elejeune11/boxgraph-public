# Extent of the intrinsic volume conservation region (App. A, Fig. 6b), found by bisection on the
# conditions coded in volume_conservation_region (built_from). The paper prints the bounds as fractions
# (-16/9, omega = 64/9, sqrt(omega) = 8/3); the outputs are 9 b_min, 9 omega and 3 sqrt(omega).
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "volume_conservation_region" / "model.py"
_spec = importlib.util.spec_from_file_location("haas2021_volume_conservation_region", _path)
_reg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_reg)


def _bisect(ok, lo, hi, tol=1e-12):
    """ok(lo) is True, ok(hi) is False: the boundary between them."""
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo


def _nonempty(b):
    return _reg.a_max(b) is not None


def _amax(b):
    a = _reg.a_max(b)
    return float("-inf") if a is None else a


def run(inputs, settings):
    # lower bound: Eq. A37b has a positive real root
    b_min = -_bisect(lambda c: _reg.thickness_root(-c) is not None, 0.0, 10.0)
    # upper bound omega: the region is non-empty
    omega = _bisect(_nonempty, 0.0, 100.0)
    # sup |H0 h|: largest a_max over a grid of b in [b_min, omega], the end points included
    n = 2000
    bs = [b_min + (omega - b_min) * i / n for i in range(1, n)] + [omega]
    a_sup = float(max(_amax(b) for b in bs))
    return {"b_min_x9": 9 * b_min, "omega_x9": 9 * omega, "sqrt_omega_x3": 3 * a_sup}
