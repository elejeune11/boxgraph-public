"""yong2025's time-varying microvascular resistance restated in our own code from the paper (Eq. 9 with
the ventricular activation e_v(t) of Eq. 4), to check the code's block against the paper it cites:

  Rmicro(t) = [ (sqrt(Rmicro,max) - sqrt(Rmicro,min)) e_v(t) + sqrt(Rmicro,min) ]^2
  e_v(t) = (1 - cos(pi t / Tvc)) / 2          0 <= t <= Tvc
           (1 + cos(pi (t - Tvc) / Tvr)) / 2  Tvc < t <= Tvc + Tvr
           0                                  Tvc + Tvr < t <= T

Its time average over one cycle, in closed form: on each of the two cosine phases e_v averages 1/2 and
e_v^2 averages 3/8, so with a = sqrt(Rmicro,min), d = sqrt(Rmicro,max) - a,
  mean = a^2 + (Tvc + Tvr)/T (a d + 3 d^2 / 8),   peak = Rmicro,max (e_v reaches 1 at t = Tvc).
"""
import math


def run(inputs, settings):
    a = math.sqrt(inputs["Ram_min"])
    d = math.sqrt(inputs["Ram_max"]) - a
    frac = (inputs["T_vc"] + inputs["T_vr"]) / inputs["T"]
    return {"Ram_mean": a * a + frac * (a * d + 3.0 * d * d / 8.0), "Ram_peak": (a + d) ** 2}


def symbolic():
    import sympy as sp

    Ram_min, Ram_max, T_vc, T_vr, T = sp.symbols("Ram_min Ram_max T_vc T_vr T", positive=True)
    a = sp.sqrt(Ram_min)
    d = sp.sqrt(Ram_max) - a
    return {"Ram_mean": a**2 + (T_vc + T_vr) / T * (a * d + sp.Rational(3, 8) * d**2), "Ram_peak": (a + d) ** 2}
