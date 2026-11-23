def run(inputs, settings):
    return {"knuc": inputs["knuc0"] * (inputs["AG"] / inputs["Atotal"]) ** 4}


def symbolic():
    import sympy as sp
    knuc0, AG, Atotal = sp.symbols("knuc0 AG Atotal", positive=True)
    return {"knuc": knuc0 * (AG / Atotal) ** 4}
