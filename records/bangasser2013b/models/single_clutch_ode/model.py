# Single-clutch master-equation ODEs of Bangasser and Odde 2013 (Eqs. 1, 2, 4-7), from the unbound,
# unloaded state (Supplement: 'The clutch is initially set in the unbound state').
# With all nc clutches alike, Eq. 4 gives xs = kc nc xc/(ks + nc kc) = a xc, and Eq. 7
# gives dxc/dt = pb vf / (1 - (1 - pb) a). The off-rate is the Bell form of Eq. 5 at the clutch's
# force Fc = kc (xc - xs). Units: pN, nm, s.
import math

from scipy.integrate import solve_ivp


def run(inputs, settings):
    p = inputs
    nm, Fm, vu, nc = p["nm"], p["Fm"], p["vu"], p["nc"]
    kon, koff, Fb, kc, ks = p["kon"], p["koff"], p["Fb"], p["kc"], p["ks"]
    a = kc * nc / (ks + nc * kc)

    def rhs(t, y):
        pb, xc = y
        Fc = kc * (1 - a) * xc
        vf = vu * (1 - ks * a * xc / (nm * Fm))
        return [(1 - pb) * kon - pb * koff * math.exp(Fc / Fb), pb * vf / (1 - (1 - pb) * a)]

    t = float(p["t"])
    if t > 0:
        sol = solve_ivp(rhs, [0.0, t], [0.0, 0.0], method="LSODA",
                        rtol=float(settings.get("rtol", 1e-8)), atol=float(settings.get("atol", 1e-12)))
        pb, xc = sol.y[0, -1], sol.y[1, -1]
    else:
        pb, xc = 0.0, 0.0
    Fc = kc * (1 - a) * xc
    return {"pb": pb, "xs": a * xc, "Fc": Fc, "vf": vu * (1 - ks * a * xc / (nm * Fm)),
            "koff_i": koff * math.exp(Fc / Fb)}
