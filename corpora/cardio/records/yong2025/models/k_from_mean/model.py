# k of Eqs. 10-11 "determined such that mean Rmicro(t) match the desired constant resistance":
# solve mean over the cycle of [(sqrt(k) - sqrt(f)) e + sqrt(f)]^2 = 1 (kPH = 1), with
# mean(e) = (Tvc + Tvr)/(2T) and mean(e^2) = 3(Tvc + Tvr)/(8T) for Eq. 4.
# Port units: percent, s.
import math


def run(inputs, settings):
    f = inputs["frac"] / 100.0
    D = (inputs["Tvc"] + inputs["Tvr"]) / inputs["T"]
    m1, m2 = D / 2.0, 3.0 * D / 8.0
    c = math.sqrt(f)
    # m2 s^2 + 2 c m1 s + (f - 1) = 0, s = sqrt(k) - sqrt(f) > 0
    s = (-2.0 * c * m1 + math.sqrt((2.0 * c * m1) ** 2 - 4.0 * m2 * (f - 1.0))) / (2.0 * m2)
    return {"k": (s + c) ** 2}
