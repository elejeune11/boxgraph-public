def run(inputs, settings):
    return {"dp": inputs["p_max"] - inputs["p_min"]}


def symbolic():
    import sympy as sp
    p_max, p_min = sp.symbols("p_max p_min", positive=True)
    return {"dp": p_max - p_min}
