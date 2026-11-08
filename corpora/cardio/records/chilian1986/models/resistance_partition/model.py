# Series resistances carrying one flow: the pressure left at a site, as a percentage of the
# aortic pressure, is the share of total resistance downstream of it (venous pressure taken as 0).


def run(inputs, settings):
    return {"proximal": 100.0 - inputs["pct"], "distal": inputs["pct"]}


def symbolic():
    import sympy as sp
    pct = sp.symbols("pct", positive=True)
    return {"proximal": 100 - pct, "distal": pct}
