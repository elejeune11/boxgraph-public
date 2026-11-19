# Intrinsic volume conservation region of App. A (Eqs. A36, A37b and the conditions stated in words
# after them). Scaled by the undeformed thickness h: b = K0 h^2, a = H0 h, X = H0/h (H0 the intrinsic
# thickness). Eq. (A37b) becomes X + b X^3/12 = 1 (the smaller positive root is taken); zeta(Z0) must
# increase on |Z0| <= H0/2, i.e. 1 - 2 a z + b z^2 >= 0 for |z| <= X/2 (z = Z0/h); and a^2 >= b.
# a_max(b) is the largest |H0 h| allowed at that b (None if no a is allowed). Solved by bisection.
import numpy as np


def thickness_root(b):
    """Smallest positive real root X of X + b X^3/12 = 1, or None."""
    if b == 0:
        return 1.0
    r = np.roots([b / 12.0, 0.0, 1.0, -1.0])
    pos = sorted(x.real for x in r if abs(x.imag) < 1e-12 * max(1.0, abs(x)) and x.real > 0)
    return pos[0] if pos else None


def monotone(a, b, X):
    """The turning points of zeta (roots of 1 - 2 a z + b z^2, a double root included) lie outside
    |z| < X/2, as the paper states the condition (Z0_+- compared with H0/2). For a >= 0 and a^2 >= b the
    binding one is the smallest positive root, 1/(a + sqrt(a^2 - b))."""
    s = a + np.sqrt(max(a * a - b, 0.0))
    if s == 0:
        return True  # a = b = 0: zeta = Z0, no turning point
    return 1.0 / s >= X / 2 - 1e-15


def a_max(b, tol=1e-13):
    X = thickness_root(b)
    if X is None:
        return None
    lo = np.sqrt(b) if b > 0 else 0.0
    if not monotone(lo, b, X):
        return None
    hi = lo + 1.0
    while monotone(hi, b, X):
        hi *= 2
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if monotone(mid, b, X):
            lo = mid
        else:
            hi = mid
    return lo


def run(inputs, settings):
    return {"a_max": a_max(inputs["b"])}
