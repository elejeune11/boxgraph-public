def run(inputs, settings):
    return {"Q_total": inputs["Q_LAD"] + inputs["Q_LCX"] + inputs["Q_RCA"]}


def symbolic():
    import sympy as sp
    a, b, c = sp.symbols("Q_LAD Q_LCX Q_RCA", positive=True)
    return {"Q_total": a + b + c}
