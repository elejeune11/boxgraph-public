import cmath
import math


def run(inputs, settings):
    r1, r2, c1, f = inputs["R1"], inputs["R2"], inputs["C1"], inputs["f"]
    w = 2 * math.pi * f
    # lambda_q dq/dt + q = alpha (lambda_p dp/dt + p) with the coefficients printed on p. 73
    lam_q = r1 * r2 * c1 / (r1 + r2)
    alpha = 1 / (r1 + r2)
    lam_p = r2 * c1
    z = (1 + 1j * w * lam_q) / (alpha * (1 + 1j * w * lam_p))
    return {"modulus": abs(z), "phase": math.degrees(cmath.phase(z))}


def symbolic():
    import sympy as sp

    R1, R2, C1, f = sp.symbols("R1 R2 C1 f", positive=True)
    w = 2 * sp.pi * f
    lam_q = R1 * R2 * C1 / (R1 + R2)
    alpha = 1 / (R1 + R2)
    lam_p = R2 * C1
    # Z = (1 + j w lam_q)/(alpha (1 + j w lam_p)), split into real and imaginary parts
    den = alpha * (1 + (w * lam_p) ** 2)
    re = (1 + w**2 * lam_q * lam_p) / den
    im = w * (lam_q - lam_p) / den
    return {"modulus": sp.sqrt(re**2 + im**2), "phase": sp.atan2(im, re) * 180 / sp.pi}
