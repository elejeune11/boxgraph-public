# Port of Cell1DPublish.cpp line 411 (divided by dt).


def run(inputs, settings):
    return {"vactin": inputs["vmax"] * inputs["PolyFactor"] * (inputs["AG"] / inputs["Atotal"])}


def symbolic():
    import sympy as sp
    vmax, PolyFactor, AG, Atotal = sp.symbols("vmax PolyFactor AG Atotal", positive=True)
    return {"vactin": vmax * PolyFactor * AG / Atotal}
