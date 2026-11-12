# Krogh radius: the circle whose area is the tissue area per capillary, 1/CD.
import math


def run(inputs, settings):
    cd_per_um2 = inputs["CD"] * 1e-6  # 1/mm^2 -> 1/um^2
    return {"R": 1.0 / math.sqrt(math.pi * cd_per_um2)}


def symbolic():
    import sympy as sp
    CD = sp.symbols("CD", positive=True)
    return {"R": 1 / sp.sqrt(sp.pi * CD * sp.Rational(1, 10**6))}
