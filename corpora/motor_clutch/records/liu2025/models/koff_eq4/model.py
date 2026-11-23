"""Two-term catch-bond dissociation rate of the integrin-fibronectin bond (Methods, Eq. 4):
koff(F) = k0off exp(beta xt F) + k0'off exp(beta x't F), beta = 1/kBT.
Units: rates 1/s, distances nm, kT pN*nm, F pN.
"""
import math


def run(inputs, settings):
    F, kT = inputs["F"], inputs["kT"]
    return {"koff": inputs["k0off"] * math.exp(inputs["xt"] * F / kT)
            + inputs["k0offp"] * math.exp(inputs["xtp"] * F / kT)}


def symbolic():
    import sympy as sp
    k0off, k0offp, xt, xtp, kT, F = sp.symbols("k0off k0offp xt xtp kT F")
    return {"koff": k0off * sp.exp(xt * F / kT) + k0offp * sp.exp(xtp * F / kT)}
