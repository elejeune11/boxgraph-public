def run(inputs, settings):
    return {"Q_ex": inputs["Q_rest"] * inputs["r"] / 100.0}


def symbolic():
    import sympy as sp
    Q, r = sp.symbols("Q_rest r", positive=True)
    return {"Q_ex": Q * r / 100}
