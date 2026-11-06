"""Pulsatility index distal to a stenosis normalised to the index of the normal leg, PI/PI0 (p. 8)."""


def run(inputs, settings):
    return {"ratio": inputs["PI"] / inputs["PI0"]}


def symbolic():
    import sympy as sp

    PI, PI0 = sp.symbols("PI PI0", positive=True)
    return {"ratio": PI / PI0}
