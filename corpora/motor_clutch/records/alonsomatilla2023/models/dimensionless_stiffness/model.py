# K = ks / (nc kc); ks in pN/um is converted to pN/nm (x 1e-3).


def run(inputs, settings):
    return {"K": inputs["ks"] * 1e-3 / (inputs["nc"] * inputs["kc"])}


def symbolic():
    import sympy as sp
    ks, nc, kc = sp.symbols("ks nc kc", positive=True)
    return {"K": ks * sp.Rational(1, 1000) / (nc * kc)}
