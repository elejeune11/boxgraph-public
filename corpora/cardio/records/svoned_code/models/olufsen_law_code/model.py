# Port of the release's OLUFSEN material (Code/Source/cvOneDMaterialOlufsen.cxx): GetEHR (lines 135-139),
# Getr1 for a uniform segment (lines 154-162) and GetPressure (lines 195-203), line by line. Our code.
import math


def run(inputs, settings):
    k1, k2, k3 = inputs["k1"], inputs["k2"], inputs["k3"]
    ro = inputs["r0"]                                  # Getr1: uniform segment, r_top = r_bot = r0
    EHR = 4.0 / 3.0 * (k1 * math.exp(k2 * ro) + k3)   # GetEHR, line 137
    So_ = ro * ro * math.pi                            # GetS1, line 150
    press = inputs["p_ref"] + EHR * (1.0 - math.sqrt(So_ / inputs["S"]))   # GetPressure, line 200
    return {"p": press}


def symbolic():
    import sympy as sp
    k1, k2, k3, r0, p_ref, S = sp.symbols("k1 k2 k3 r0 p_ref S", real=True)
    return {"p": p_ref + sp.Rational(4, 3) * (k1 * sp.exp(k2 * r0) + k3) * (1 - sp.sqrt(sp.pi * r0 ** 2 / S))}
