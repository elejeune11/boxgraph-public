# sigma* = dmu0/dr; J/m^2 over nm = 1e9 Pa = 1e6 kPa


def run(inputs, settings):
    return {"sigma_star": inputs["dmu0"] / inputs["dr"] * 1e6}


def symbolic():
    import sympy as sp
    dmu0, dr = sp.symbols("dmu0 dr", positive=True)
    return {"sigma_star": dmu0 / dr * 10**6}
