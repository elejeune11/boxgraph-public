# k~s = ks l0 / f with l0 = (kBT/(wd0 Gamma))^1/2 [nm] and f = (wd0 Gamma kBT)^1/2 [pN] (p. 3).
import math


def run(inputs, settings):
    wd0, kT = inputs["wd0"], inputs["kT"]
    gam = inputs["Gamma_kT"] * kT
    l0 = math.sqrt(kT / (wd0 * gam))
    f = math.sqrt(wd0 * gam * kT)
    return {"ks_nd": inputs["ks"] * l0 / f}
