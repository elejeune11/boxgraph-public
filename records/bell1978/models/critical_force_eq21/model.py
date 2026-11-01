import math

EV_NM_DYNE = 1.602176634e-12 / 1e-7  # eV/nm -> dyne


def run(inputs, settings):
    scale = inputs["kT"] / inputs["r0"] * EV_NM_DYNE
    coeff = 0.7 * scale
    return {"force_scale": scale, "log_coefficient": coeff, "fc": coeff * math.log(inputs["KN2"])}


def symbolic():
    import sympy as sp
    kT, r0, KN2 = sp.symbols("kT r0 KN2", positive=True)
    scale = kT / r0 * EV_NM_DYNE
    return {"force_scale": scale, "log_coefficient": sp.Rational(7, 10) * scale,
            "fc": sp.Rational(7, 10) * scale * sp.log(KN2)}
