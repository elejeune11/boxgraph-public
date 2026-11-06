# Root input impedance of the asymmetric structured tree, as printed (cgs units throughout).
# A vessel of radius r has length lrr*r, compliance C = 3 A0 r/(2 Eh) with Eh/r from Eq. 6,
# the Womersley factor K of Eq. 12 (piecewise, as printed, principal branch of i^-1/2),
# and input impedance from Eq. 16 with Z(L) the parallel combination (Eq. 17) of its two
# daughters (radii alpha*r and beta*r). Branching stops at a vessel whose radius is less than
# r_min ("the tree is terminated whenever the radius of the leaves is less than some given
# minimum radius"): that vessel is a leaf, with the zero impedance the paper assumes at its end.
# omega = 0 uses the DC limit of Eq. 18 for each vessel.
import cmath
import math


def run(inputs, settings):
    r_root, r_min, lrr = inputs["r_root"], inputs["r_min"], inputs["lrr"]
    xi, gam = inputs["xi"], inputs["gamma"]
    k1, k2, k3 = inputs["k1"], inputs["k2"], inputs["k3"]
    nu, rho, om = inputs["nu"], inputs["rho"], inputs["omega"]
    mu = nu * rho
    alpha = (1 + gam ** (xi / 2)) ** (-1 / xi)
    beta = alpha * math.sqrt(gam)
    i_m12 = cmath.exp(-1j * math.pi / 4)  # i^(-1/2)

    memo = {}

    def Z(n_a, n_b):
        key = (n_a, n_b)
        if key in memo:
            return memo[key]
        r = r_root * alpha ** n_a * beta ** n_b
        if r < r_min:
            zl = 0j
        else:
            zl = 1 / (1 / Z(n_a + 1, n_b) + 1 / Z(n_a, n_b + 1))
        L = lrr * r
        if om == 0:
            z = 8 * mu * lrr / (math.pi * r ** 3) + zl
        else:
            A0 = math.pi * r ** 2
            Eh = (k1 * math.exp(k2 * r) + k3) * r
            C = 3 * A0 * r / (2 * Eh)
            w = r * math.sqrt(om / nu)
            K = 1 - 2 * i_m12 / w if w > 4 else 1 / (4 / 3 - 8j / w ** 2)
            c = cmath.sqrt(A0 * K / (rho * C))
            g = cmath.sqrt(C * A0 * K / rho)
            s, co = cmath.sin(om * L / c), cmath.cos(om * L / c)
            z = (1j / g * s + zl * co) / (co + 1j * g * zl * s)
        memo[key] = z
        return z

    z0 = Z(0, 0)
    return {"Zmod": abs(z0), "Zphase": math.degrees(cmath.phase(z0))}
