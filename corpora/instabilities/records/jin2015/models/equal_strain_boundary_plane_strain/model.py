# The boundary of equal critical strain (Sec. 2, Fig. 3(a)): the modulus ratio Gf/Gs at
# which the minimal wrinkling strain e_m (Eqs. B7-B15) equals the critical strain for the
# onset of creases, at a given thickness ratio. Plane strain. The paper does not say how
# it located the curve; bisection in log(Gf/Gs) on e_m(Gf/Gs) - e_crease is the reader's.
import importlib.util
import math
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkle_eigen_plane_strain" / "model.py"
_spec = importlib.util.spec_from_file_location("jin2015_wrinkle_eigen_plane_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def boundary(r, e_crease, loading, settings):
    g_lo, g_hi = settings.get("g_lo", 1.0), settings.get("g_hi", 20.0)
    tol = settings.get("g_tol", 1e-4)
    em = lambda g: _base.solve(g, r, loading, settings)["em"]  # noqa: E731
    lo, hi = math.log(g_lo), math.log(g_hi)
    if em(g_lo) < e_crease or em(g_hi) > e_crease:
        return float("nan")
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if em(math.exp(mid)) > e_crease:
            lo = mid
        else:
            hi = mid
    return math.exp(0.5 * (lo + hi))


def run(inputs, settings):
    return {"Gf_Gs": boundary(inputs["Hs_Hf"], inputs["e_crease"], "plane_strain", settings)}
