# The bracket of B in Eq. B25 set to zero at g = gb (p. 7), solved for eta. As a quadratic in eta:
# (gb^6 + 3 gb^4 - gb^2 + 1) eta^2 + (-2 gb^4 + 4 gb^2 - 2) eta - 4 gb^2 = 0; the constant term is
# negative, so there is one positive root. Solved numerically, independently of the closed form B28.
import numpy as np


def run(inputs, settings):
    g = inputs["gb"]

    def bracket(eta):
        return g**6 * eta**2 + g**4 * eta * (3 * eta - 2) - g**2 * (eta - 2) ** 2 + (eta - 2) * eta

    # fit the quadratic from three evaluations of the printed bracket, so the expansion is not hand-made
    xs = np.array([0.0, 1.0, 2.0])
    c = np.polyfit(xs, [bracket(x) for x in xs], 2)
    roots = [r.real for r in np.roots(c) if abs(r.imag) < 1e-12 and r.real > 0]
    return {"eta_b": float(min(roots))}
