# Eqs. (2), (3), (5) with the mantle stress of Appendix E (Eqs. E.1-E.4): circular growing elastic
# mantle ring attached to the shell edge; the stress n3 changes the deposition angle phi.
# All quantities are in the paper's nondimensional units.
# Output: time and shell radius of the n-th maximum of r_s(t) (the n-th rib), 0 < t <= t_max.
import math

from scipy.integrate import solve_ivp


def n3(rs, gamma, a0, EA, ks):
    # (1/a) EA (a/(gamma a0) - 1) + ks (a - rs) = 0  ->  ks a^2 + (EA/(gamma a0) - ks rs) a - EA = 0
    b = EA / (gamma * a0) - ks * rs
    a = (-b + math.sqrt(b * b + 4.0 * ks * EA)) / (2.0 * ks)
    return EA * (a / (gamma * a0) - 1.0)


def H(n, rs, p):
    return p["kphi"] * (1.0 - math.exp(p["K"] * n))      # Eq. (5): H2 = k_phi (1 - e^{K n3})


def run(inputs, settings):
    p = inputs
    n_rib = int(round(p["n"]))

    def rhs(t, y):
        rs, phi = y
        gamma = p["gamma0"] + p["gamma_rate"] * t
        return [p["kg"] * math.cos(p["theta"]) * math.sin(phi), H(n3(rs, gamma, p["a0"], p["EA"], p["ks"]), rs, p)]

    def top(t, y):
        return y[1]
    top.direction = -1

    sol = solve_ivp(rhs, (0.0, settings["t_max"]), [p["rs0"], p["phi0"]], method="LSODA", events=top,
                    rtol=settings["rtol"], atol=settings["rtol"] * 1e-2)
    te, ye = sol.t_events[0], sol.y_events[0]
    if n_rib < 1 or n_rib > len(te):
        return {"t_rib": None, "r_rib": None}
    return {"t_rib": float(te[n_rib - 1]), "r_rib": float(ye[n_rib - 1][0])}
