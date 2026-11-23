# Table 2 definitions. vu [nm/s] kc [pN/nm] / (Fb [pN] koff [1/s]) is dimensionless.


def run(inputs, settings):
    i = inputs
    return {"F": i["nm"] * i["Fm"] / (i["nc"] * i["Fb"]),
            "tau": i["kon"] / i["koff"],
            "omega": i["vu"] * i["kc"] / (i["Fb"] * i["koff"]),
            "Delta": i["Fth"] / i["Fb"]}


def symbolic():
    import sympy as sp
    nm, Fm, nc, Fb, kon, koff, vu, kc, Fth = sp.symbols("nm Fm nc Fb kon koff vu kc Fth", positive=True)
    return {"F": nm * Fm / (nc * Fb), "tau": kon / koff, "omega": vu * kc / (Fb * koff), "Delta": Fth / Fb}
