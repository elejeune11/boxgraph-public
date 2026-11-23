# The logic of stable_size_chain, applied to the printed E*FA curve whose ECM modulus equals E.
# The growth rate J has the sign of sigma(rFA) - sigma*, since h (rc - rFA) > 0 for rFA < rc.
# The stable size is the largest rFA where sigma - sigma* falls from >= 0 to < 0 along the curve,
# interpolated linearly between the curve's points. No such crossing, or no curve at E: NaN.


def _sigma(Keff, K, rho0, a, b):
    g = K * b - 1.0
    return 1.0 / (1.0 / Keff + (b - a) / g) * b * rho0 / g


def _stable(curve, En, K, rho0, a, b, s_star):
    pts = sorted(zip(curve["x"], curve["y"]))
    f = [(r, _sigma(1.0 / (1.0 / En + 1.0 / e), K, rho0, a, b) - s_star if e > 0 else -s_star) for r, e in pts]
    r_st = float("nan")
    for (r0, f0), (r1, f1) in zip(f, f[1:]):
        if f0 >= 0 > f1:
            r_st = r0 + (r1 - r0) * f0 / (f0 - f1)
    return r_st


def run(inputs, settings):
    a, b = inputs["alpha"] * 1e3, inputs["beta"] * 1e3   # per Pa -> per kPa
    s_star = inputs["dmu0"] / inputs["dr"] * 1e6          # J/m^2 / nm -> Pa -> kPa (x1e9 / 1e3)
    E = inputs["E"]
    for key in ("a", "b"):
        if abs(inputs["E_" + key] - E) < 1e-9 * max(1.0, abs(E)):
            return {"r_st": _stable(inputs["Efa_" + key], inputs["En"], inputs["K"], inputs["rho0"], a, b, s_star)}
    return {"r_st": float("nan")}
