# Port of cvOneDMaterial::SetProfileExponent and UpdateKinematicViscosity (Code/Source/cvOneDMaterial.h,
# lines 99-107), line by line. Our code.
import math


def run(inputs, settings):
    kinematicViscosity = inputs["mu"] / inputs["rho"]              # UpdateKinematicViscosity, line 107
    profile_exponent = inputs["n"]
    delta = 1.0 / (1.0 + profile_exponent)                          # line 100
    myPI = 4.0 * math.atan(1.0)                                     # line 101
    N = -2.0 * myPI * kinematicViscosity * (profile_exponent + 2.0)  # line 102
    return {"delta": delta, "N": N}


def symbolic():
    import sympy as sp
    mu, rho, n = sp.symbols("mu rho n", positive=True)
    return {"delta": 1 / (1 + n), "N": -2 * sp.pi * (mu / rho) * (n + 2)}
