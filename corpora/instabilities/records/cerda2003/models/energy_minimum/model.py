# Minimize the printed energy U(k) = B k^2 Delta L + pi^2 T Delta / (k^2 L) over k numerically
# (in s = ln k, where dU/ds changes sign once), then lambda = 2 pi / k. SI units.
import math

from scipy.optimize import brentq


def run(inputs, settings):
    B, T, L, D = inputs["B"], inputs["T"], inputs["L"], inputs["Delta"]
    a = B * D * L
    b = math.pi**2 * T * D / L

    def dU_ds(s):  # U(s) = a e^{2s} + b e^{-2s}
        return 2.0 * a * math.exp(2.0 * s) - 2.0 * b * math.exp(-2.0 * s)

    s = brentq(dU_ds, settings["s_lo"], settings["s_hi"], xtol=settings["xtol"], rtol=1e-15, maxiter=500)
    return {"lam": 2.0 * math.pi / math.exp(s)}
