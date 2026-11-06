def run(inputs, settings):
    # the text's value does not depend on where the figure is read
    return {"V_max": inputs["V_max"]}


def symbolic():
    import sympy as sp
    v = sp.Symbol("V_max", real=True)
    return {"V_max": v}
