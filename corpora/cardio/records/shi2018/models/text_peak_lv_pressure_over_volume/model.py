def run(inputs, settings):
    # the text's value does not depend on where the figure is read
    return {"P_max": inputs["P_max"]}


def symbolic():
    import sympy as sp
    v = sp.Symbol("P_max", real=True)
    return {"P_max": v}
