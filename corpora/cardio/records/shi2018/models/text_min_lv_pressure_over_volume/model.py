def run(inputs, settings):
    # the text's value does not depend on where the figure is read
    return {"P_min": inputs["P_min"]}


def symbolic():
    import sympy as sp
    v = sp.Symbol("P_min", real=True)
    return {"P_min": v}
