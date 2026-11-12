# Diffusion radius = sqrt(1 / (pi * Lv)), read with pi x length density as the divisor
# (the left-to-right reading has the wrong dimension; see question q_radius_precedence).
# Lv in mm/mm^3 = 1/mm^2, so the root is in mm; the port is um.
import math


def run(inputs, settings):
    return {"R": 1000.0 * math.sqrt(1.0 / (math.pi * inputs["Lv"]))}


def symbolic():
    import sympy as sp
    Lv = sp.symbols("Lv", positive=True)
    return {"R": 1000 * sp.sqrt(1 / (sp.pi * Lv))}
