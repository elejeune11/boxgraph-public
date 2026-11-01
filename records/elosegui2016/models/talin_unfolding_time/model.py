# Mean unfolding time of a first-order (exponential) process with the slip-bond rate k_unf(f): t = 1/k_unf.
# f is the force on talin itself (the clutch model applies k_unf to FR times the integrin force). Our code.
import math


def run(inputs, settings):
    return {"t": math.exp(-(inputs["ln_kunf0"] + inputs["kunf_b"] * inputs["f"]))}


def symbolic():
    import sympy as sp
    a, b, f = sp.symbols("ln_kunf0 kunf_b f")
    return {"t": sp.exp(-(a + b * f))}
