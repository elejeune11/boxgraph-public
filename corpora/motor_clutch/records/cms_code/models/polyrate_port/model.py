# Port of cms2Dv1_0.m line 371 (our code): polyrate = maxpoly*(1-(factin/totact)).


def run(inputs, settings):
    return {"vp": inputs["maxpoly"] * (1 - inputs["factin"] / inputs["totact"])}


def symbolic():
    import sympy as sp
    maxpoly, factin, totact = sp.symbols("maxpoly factin totact", positive=True)
    return {"vp": maxpoly * (1 - factin / totact)}
