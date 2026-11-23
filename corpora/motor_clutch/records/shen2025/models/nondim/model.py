# Dimensionless parameters of Sec. II B (p. 3): l0 = (kBT/(wd0 Gamma))^1/2 [nm], f = (wd0 Gamma kBT)^1/2 [pN].
# Gamma_kT is Gamma/(kB T) in s/nm^2, so Gamma = Gamma_kT * kT in pN s/nm.
import math


def run(inputs, settings):
    wd0, kT = inputs["wd0"], inputs["kT"]
    gam = inputs["Gamma_kT"] * kT                 # pN s / nm
    l0 = math.sqrt(kT / (wd0 * gam))              # nm
    f = math.sqrt(wd0 * gam * kT)                 # pN
    return {
        "w": inputs["wa"] / wd0,
        "kon_nd": inputs["kon"] / wd0,
        "koff_nd": inputs["koff"] / wd0,
        "fs_nd": inputs["fs"] / f,
        "fd_nd": inputs["fd"] / f,
        "Fb_nd": inputs["Fb"] / f,
        "km_nd": inputs["km"] * l0 / f,
        "kc_nd": inputs["kc"] * l0 / f,
    }
