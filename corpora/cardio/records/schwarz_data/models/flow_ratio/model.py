# Our own arithmetic: one flow over another.
def run(inputs, settings):
    return {"ratio": inputs["Q_1"] / inputs["Q_2"]}


def symbolic():
    import sympy as sp
    Q_1, Q_2 = sp.symbols("Q_1 Q_2", positive=True)
    return {"ratio": Q_1 / Q_2}
