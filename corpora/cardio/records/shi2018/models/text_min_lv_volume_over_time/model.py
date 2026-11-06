def run(inputs, settings):
    # the text's value does not depend on where the figure is read
    return {"V_min": inputs["V_min"]}


def symbolic():
    import sympy as sp
    v = sp.Symbol("V_min", real=True)
    return {"V_min": v}
