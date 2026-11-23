# Characteristic scales of Sec. II B (p. 3). With Gamma/(kB T) given in s/nm^2, kB T cancels from l0 and
# f/(kB T): l0 = (1/(wd0 * Gamma/kBT))^1/2, f/kBT = (wd0 * Gamma/kBT)^1/2.
import math


def run(inputs, settings):
    wd0, g = inputs["wd0"], inputs["Gamma_kT"]
    l0 = math.sqrt(1.0 / (wd0 * g))
    return {"l0": l0, "tau": 1.0 / wd0, "v0": l0 * wd0, "f_kT": math.sqrt(wd0 * g)}


def symbolic():
    import sympy as sp
    wd0, g = sp.symbols("wd0 Gamma_kT", positive=True)
    l0 = sp.sqrt(1 / (wd0 * g))
    return {"l0": l0, "tau": 1 / wd0, "v0": l0 * wd0, "f_kT": sp.sqrt(wd0 * g)}
