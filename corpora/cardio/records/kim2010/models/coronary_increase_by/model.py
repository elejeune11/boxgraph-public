def run(inputs, settings):
    return {"Q_ex": inputs["Q_rest"] * (1.0 + inputs["r"] / 100.0)}


def symbolic():
    import sympy as sp
    Q, r = sp.symbols("Q_rest r", positive=True)
    return {"Q_ex": Q * (1 + r / 100)}
