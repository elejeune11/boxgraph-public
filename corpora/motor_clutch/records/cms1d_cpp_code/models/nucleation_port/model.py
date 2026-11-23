# Port of Cell1DPublish.cpp line 628.


def run(inputs, settings):
    return {"knuc": (inputs["AG"] / inputs["Atotal"]) ** 4 * inputs["knuc0"]}


def symbolic():
    import sympy as sp
    knuc0, AG, Atotal = sp.symbols("knuc0 AG Atotal", positive=True)
    return {"knuc": (AG / Atotal) ** 4 * knuc0}
