# The red dashed scaling of Fig. 2B as labelled, C proportional to N^2, with N the number of vessels of a
# full, balanced tree of depth B (the caption: "Plots reference bifurcation depth in full, balanced
# trees"): a tree whose bifurcations reach depth B has N = 2^(B+1) - 1 vessels. C0 is the cost of the
# one-vessel tree (B = 0), the proportionality constant, which the paper does not state.
def run(inputs, settings):
    n = 2.0 ** (inputs["B"] + 1.0) - 1.0
    return {"C": inputs["C0"] * n * n}


def symbolic():
    import sympy as sp

    B, C0 = sp.symbols("B C0", positive=True)
    return {"C": C0 * (2 ** (B + 1) - 1) ** 2}
