"""Ratio of two myosin densities (Results, p. 14): ratio = sm_a / sm_b."""


def run(inputs, settings):
    return {"ratio": inputs["sm_a"] / inputs["sm_b"]}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("sm_a sm_b", positive=True)
    return {"ratio": a / b}
