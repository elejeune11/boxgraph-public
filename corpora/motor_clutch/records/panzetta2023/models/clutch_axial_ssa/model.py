# Modified motor-clutch model with an orthogonal substrate spring, residual strain applied axially
# (Eqs. 2-6, 10, 11), simulated by the Gillespie algorithm of Eq. 12 and Sec. 2.2.
# Units: nm, pN, s. Positions and forces positive in the retrograde direction.
#
# Per event (Sec. 2.2): every clutch draws t_i = -ln(random_i)/k_i (Eq. 12), k_i = kon if free,
# koff exp(Fc_i/Fb) if engaged (Eq. 3), Fc_i = kc (x_c,i - x_s) (Eq. 4); the shortest event is
# executed and time advances by it; engaged clutches advance by v_f dt; a clutch that engages starts
# at the substrate position; x_s solves the force balance sum Fc_i = Fs (Eq. 5, axial; Eq. 7,
# transverse); v_f = vu (1 - F/(nm Fm)) (Eq. 10).
import math

import numpy as np


def ortho_force(x, ke, l, L):
    """Horizontal force of the orthogonal spring (rest length l) whose ends are a vertical distance L
    apart, when P1 is displaced horizontally by x: ke (sqrt(L^2 + x^2) - l) x / sqrt(L^2 + x^2)
    (the first term of Eq. 6), and its derivative in x."""
    r = math.sqrt(L * L + x * x)
    f = ke * (r - l) * x / r
    df = ke * (1.0 - l * L * L / (r * r * r))
    return f, df


def solve_xs(S, n, p, x_guess):
    """x_s from kc (S - n x_s) + F0 = ks (x_off + x_s) + ortho(x_off + x_s) by Newton's method,
    where S is the sum of engaged clutch positions and n their number."""
    kc, ks, ke, l, L, x_off, F0 = p["kc"], p["ks"], p["ke"], p["l"], p["L"], p["x_off"], p["F0"]
    x = x_guess
    for _ in range(50):
        f, df = ortho_force(x_off + x, ke, l, L)
        g = kc * (S - n * x) + F0 - ks * (x_off + x) - f
        dg = -kc * n - ks - df
        step = g / dg
        x -= step
        if abs(step) < 1e-10 * (1.0 + abs(x)):
            break
    return x


def simulate(inputs, settings, geometry):
    """geometry: dict with L (vertical distance P1-P2), x_off (horizontal offset of P1 from above P2)
    and F0 (constant applied force in the force balance)."""
    nc = int(round(inputs["nc"]))
    nm = inputs["nm"]
    Fm, vu = inputs["Fm"], inputs["vu"]
    kon, koff, Fb, kc = inputs["kon"], inputs["koff"], inputs["Fb"], inputs["kc"]
    p = {"kc": kc, "ks": inputs["ks"], "ke": inputs["ke"], "l": inputs["l"], **geometry}
    n_events = int(settings["n_events"])
    rng = np.random.default_rng(int(settings["seed"]))
    Fstall = nm * Fm

    bound = np.zeros(nc, dtype=bool)
    x = np.zeros(nc)
    S, n = 0.0, 0
    xs = solve_xs(0.0, 0, p, 0.0)      # rest position with no clutch engaged (0 when F0 balances)
    Fload = 0.0
    v = vu
    t = 0.0
    v_int = n_int = F_int = xs_int = 0.0
    v_sum = 0.0
    n_fail = 0
    with np.errstate(over="ignore", divide="ignore"):
        for _ in range(n_events):
            k = np.where(bound, koff * np.exp(kc * (x - xs) / Fb), kon)
            tev = -np.log(rng.random(nc)) / k
            j = int(np.argmin(tev))
            dt = float(tev[j])
            # averages over the interval, in the state that held during it
            v_int += v * dt
            n_int += n * dt
            F_int += Fload * dt
            xs_int += xs * dt
            t += dt
            # engaged clutches advance with the F-actin flow
            x[bound] += v * dt
            n_before = n
            if bound[j]:
                bound[j] = False
            else:
                bound[j] = True
                x[j] = xs
            n = int(bound.sum())
            S = float(x[bound].sum()) if n else 0.0
            xs = solve_xs(S, n, p, xs)
            Fload = kc * (S - n * xs)        # sum of clutch forces, the load on the motors
            v = vu * (1.0 - Fload / Fstall)
            v_sum += v
            if n_before > 0 and n == 0:
                n_fail += 1
    T = t if t > 0 else 1.0
    return {
        "v_retro": v_int / T if settings.get("average", "time") == "time" else v_sum / n_events,
        "n_eng": n_int / T,
        "F_clutch": F_int / T,
        "x_sub": xs_int / T,
        "t_cycle": T / n_fail if n_fail else T,
    }


def axial_geometry(inputs):
    """Fig. 1B: P2 moved to P2', so the spring's ends are l (1 + eps0) apart vertically (Eq. 1);
    the applied force is balanced by the constraints (Eq. 5)."""
    return {"L": inputs["l"] * (1.0 + inputs["eps0"]), "x_off": 0.0, "F0": 0.0}


def run(inputs, settings):
    return simulate(inputs, settings, axial_geometry(inputs))
