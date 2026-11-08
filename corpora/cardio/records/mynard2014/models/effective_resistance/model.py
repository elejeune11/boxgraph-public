def run(inputs, settings):
    return {"R": (inputs["pLM"] - inputs["pRA"]) / inputs["qLM"]}


def symbolic():
    import sympy as sp
    pLM, pRA, qLM = sp.symbols("pLM pRA qLM", positive=True)
    return {"R": (pLM - pRA) / qLM}
