# Canonical clutch-ensemble ODEs of SI Appendix 1 (Eqs. 3, 4, 11, s.1-s.6), integrated over one
# load-and-fail cycle.
#
# State: Pb and <xc>. xs follows from s.4, <Fc> from Eq. 4, vf from s.5, d<xc>/dt from s.6.
# Start (Appendix 1): "when substrate position xs and the average position of the clutch <xc> are
# the same, the clutch force is null": <xc> = xs = x0. Pb(0) = 0 is the reader's choice
# (q_initial_state). The cycle ends at the abrupt failure, where r Pb Fb - <Fc> (the base of the
# power in Eq. 11) first falls to g_fail after having risen above it, as in ref. 42's ODEs.
# Output: the failure time and vf averaged over the cycle (q_flow_definition).
#
# Numerics: s.4-s.6 contain <xc> only as <xc> - x0, so the state is integrated as y = <xc> - x0
# (the same equations; it keeps a large x0 from costing digits). Units: pN, nm, s.
import numpy as np
from scipy.integrate import LSODA


def _cycle(p, settings):
    nm, Fm, vu, nc = p["nm"], p["Fm"], p["vu"], p["nc"]
    kon, koff, Fb, kc, ks, r = p["kon"], p["koff"], p["Fb"], p["kc"], p["ks"], p["r"]
    K = ks * nc * kc / (ks + nc * kc)            # s.4-s.5: Fs - F0 = K (<xc> - x0)

    def fc(y):                                    # Eq. 4 with s.4: <Fc> = kc ks/(ks + nc kc) (<xc> - x0)
        return K * y / nc

    def rhs(t, s):
        Pb, y, _ = s
        vf = vu * (1 - K * y / (nm * Fm))         # s.5
        g = r * Pb * Fb - fc(y)
        if Pb > 0 and g > 0:
            koff_mean = (1 - Pb) * koff + Pb * koff * (r * Pb * Fb / g) ** r     # Eq. 11
        else:
            koff_mean = koff
        dy = (ks + nc * kc) / (ks + Pb * nc * kc) * Pb * vf                      # s.6
        return [(1 - Pb) * kon - Pb * koff_mean, dy, vf]

    gfail = float(settings.get("g_fail", 1e-3))
    solver = LSODA(rhs, 0.0, [0.0, 0.0, 0.0], float(settings.get("t_max", 1e5)),
                   rtol=float(settings.get("rtol", 1e-8)), atol=float(settings.get("atol", 1e-12)))
    ts, ys = [0.0], [np.zeros(3)]
    risen = False
    while solver.status == "running":
        solver.step()
        ts.append(solver.t)
        ys.append(solver.y.copy())
        g = r * solver.y[0] * Fb - fc(solver.y[1])
        if g > gfail:
            risen = True
        if risen and g <= gfail:
            g0 = r * ys[-2][0] * Fb - fc(ys[-2][1])
            w = (g0 - gfail) / (g0 - g) if g0 != g else 1.0
            T = ts[-2] + w * (ts[-1] - ts[-2])
            disp = ys[-2][2] + w * (ys[-1][2] - ys[-2][2])
            return T, disp
    return None, None                              # no failure before t_max: no cycle


def run(inputs, settings):
    T, disp = _cycle(inputs, settings)
    if T is None:
        return {"t_cycle": None, "v_mean": None}
    return {"t_cycle": float(T), "v_mean": float(disp / T)}
