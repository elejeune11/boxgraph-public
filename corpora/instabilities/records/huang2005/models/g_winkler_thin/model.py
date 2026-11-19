def run(inputs, settings):
    nu = inputs["nu_s"]
    return {"g": (1 - nu) ** 2 / (1 - 2 * nu) / inputs["kH"]}


def symbolic():
    import sympy as sp
    kH, nu_s = sp.symbols("kH nu_s", positive=True)
    return {"g": (1 - nu_s) ** 2 / (1 - 2 * nu_s) / kH}
