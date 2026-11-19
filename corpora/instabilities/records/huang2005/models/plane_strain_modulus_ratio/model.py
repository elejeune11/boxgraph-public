def run(inputs, settings):
    nu, nu_s = inputs["nu"], inputs["nu_s"]
    return {"Ebar_over_Esbar": inputs["E_over_Es"] * (1 - nu_s ** 2) / (1 - nu ** 2)}


def symbolic():
    import sympy as sp
    r, nu, nu_s = sp.symbols("E_over_Es nu nu_s", positive=True)
    return {"Ebar_over_Esbar": r * (1 - nu_s ** 2) / (1 - nu ** 2)}
