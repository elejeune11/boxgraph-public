# Eq. 10: the expected time for nc parallel clutch-binding reactions, each at rate kon, to all occur.


def run(inputs, settings):
    nc = int(round(inputs["nc"]))
    kon = inputs["kon"]
    return {"tbinding": sum(1.0 / (kon * (nc - i)) for i in range(nc))}


def symbolic():
    import sympy as sp
    nc, kon = sp.symbols("nc kon", positive=True)
    return {"tbinding": sp.harmonic(nc) / kon}
