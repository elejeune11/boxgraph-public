# SI p. 11-13, in words: N cells created per mitotic time tm in a volume V, each of volume Vc,
# give a relative volume growth rate N Vc/(V tm). Volumes in pL, time in hours; rate in percent per hour.


def run(inputs, settings):
    return {"rate": 100.0 * inputs["N"] * inputs["Vc"] / (inputs["V"] * inputs["tm"])}


def symbolic():
    import sympy as sp
    N, V, Vc, tm = sp.symbols("N V Vc tm", positive=True)
    return {"rate": 100 * N * Vc / (V * tm)}
