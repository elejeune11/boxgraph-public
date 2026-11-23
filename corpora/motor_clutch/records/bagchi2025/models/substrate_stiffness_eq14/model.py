def run(inputs, settings):
    kmin, kmax = inputs["kmin"], inputs["kmax"]
    return {"ks": kmin + ((kmax - kmin) / inputs["xmax"]) * inputs["xs"]}


def symbolic():
    import sympy as sp
    kmin, kmax, xmax, xs = sp.symbols("kmin kmax xmax xs", real=True)
    return {"ks": kmin + ((kmax - kmin) / xmax) * xs}
