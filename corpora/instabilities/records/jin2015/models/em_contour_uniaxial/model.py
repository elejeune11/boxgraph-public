# A contour of Fig. 3(a): the modulus ratio Gf/Gs at which the minimal wrinkling strain under
# uniaxial compression, e_m^Uni from Eqs. B7-B15, equals a given level, at a given thickness
# ratio Hs/Hf. The paper draws the contours without saying how it located them; bisection in
# log(Gf/Gs) on e_m(Gf/Gs) - level (e_m falls as Gf/Gs grows) is the reader's.
import importlib.util
import math
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkle_eigen_plane_strain" / "model.py"
_spec = importlib.util.spec_from_file_location("jin2015_wrinkle_eigen_plane_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    r, level = inputs["Hs_Hf"], inputs["em"]
    g_lo, g_hi, tol = settings.get("g_lo", 1.0), settings.get("g_hi", 10000.0), settings.get("g_tol", 1e-3)
    em = lambda g: _base.solve(g, r, "uniaxial", settings)["em"]  # noqa: E731
    if em(g_lo) < level or em(g_hi) > level:
        raise ValueError(f"the contour e_m = {level} does not cross Gf/Gs in [{g_lo}, {g_hi}] at Hs/Hf = {r}")
    lo, hi = math.log(g_lo), math.log(g_hi)
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if em(math.exp(mid)) > level:
            lo = mid
        else:
            hi = mid
    return {"Gf_Gs": math.exp(0.5 * (lo + hi))}
