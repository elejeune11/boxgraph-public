def run(inputs, settings):
    return {"vactin": inputs["vactin_max"] * inputs["AG"] / inputs["Atotal"]}


def symbolic():
    import sympy as sp
    vactin_max, AG, Atotal = sp.symbols("vactin_max AG Atotal", positive=True)
    return {"vactin": vactin_max * AG / Atotal}
