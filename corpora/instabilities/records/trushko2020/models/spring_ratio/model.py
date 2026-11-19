def run(inputs, settings):
    return {"ratio": inputs["k_tissue"] / inputs["k_cap"]}


def symbolic():
    import sympy as sp
    kt, kc = sp.symbols("k_tissue k_cap", positive=True)
    return {"ratio": kt / kc}
