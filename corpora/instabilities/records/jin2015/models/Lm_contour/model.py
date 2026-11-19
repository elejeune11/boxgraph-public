# A contour of Fig. 3(b): the modulus ratio Gf/Gs at which the nominal wavelength at the minimal
# strain, L^m_wrinkle/Hf from Eqs. B7-B15, equals a given level, at a given thickness ratio
# Hs/Hf. The paper says L^m/Hf does not depend on the type of deformation; plane strain is used.
# The paper does not say how it located the contours. The reader's scheme: L_m grows with Gf/Gs,
# but near Gf/Gs = 1 (one homogeneous layer) the wavelength at the minimum is not defined, so the
# bracket is found by stepping down from g_hi by the factor g_step until L_m falls below the
# level, then bisecting in log(Gf/Gs).
import importlib.util
import math
import pathlib

_path = pathlib.Path(__file__).resolve().parent.parent / "wrinkle_eigen_plane_strain" / "model.py"
_spec = importlib.util.spec_from_file_location("jin2015_wrinkle_eigen_plane_strain", _path)
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)


def run(inputs, settings):
    r, level = inputs["Hs_Hf"], inputs["Lm"]
    g_lo, g_hi = settings.get("g_lo", 1.0), settings.get("g_hi", 2000.0)
    step, tol = settings.get("g_step", 1.5), settings.get("g_tol", 1e-3)
    Lm = lambda g: _base.solve(g, r, "plane_strain", settings)["Lm"]  # noqa: E731
    if Lm(g_hi) < level:
        raise ValueError(f"L_m/Hf = {level} lies above Gf/Gs = {g_hi} at Hs/Hf = {r}")
    hi = g_hi
    while True:
        lo = hi / step
        if lo < g_lo:
            raise ValueError(f"L_m/Hf = {level} not reached for Gf/Gs down to {g_lo} at Hs/Hf = {r}")
        if Lm(lo) < level:
            break
        hi = lo
    a, b = math.log(lo), math.log(hi)
    while b - a > tol:
        mid = 0.5 * (a + b)
        if Lm(math.exp(mid)) < level:
            a = mid
        else:
            b = mid
    return {"Gf_Gs": math.exp(0.5 * (a + b))}
