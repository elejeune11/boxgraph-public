def run(inputs, settings):
    return {"plc": -inputs["qc"] * inputs["Ra"] + inputs["pim"]}


def symbolic():
    import sympy as sp
    qc, Ra, pim = sp.symbols("qc Ra pim", real=True)
    return {"plc": -qc * Ra + pim}
