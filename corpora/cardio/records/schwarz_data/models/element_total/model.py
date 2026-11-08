# Our own arithmetic: TreeQ holds the internal elements (IE) and the source elements (SE); the
# elements of the network are both together (DemonstrationCode.m line 13 joins them the same way).
def run(inputs, settings):
    return {"n": inputs["n_IE"] + inputs["n_SE"]}


def symbolic():
    import sympy as sp
    n_IE, n_SE = sp.symbols("n_IE n_SE", positive=True)
    return {"n": n_IE + n_SE}
