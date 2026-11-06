def run(inputs, settings):
    return {"R": (inputs["Pao_mean"] - inputs["Pven_mean"]) / inputs["CO"]}


def symbolic():
    import sympy as sp
    Pao_mean, Pven_mean, CO = sp.symbols("Pao_mean Pven_mean CO", positive=True)
    return {"R": (Pao_mean - Pven_mean) / CO}
