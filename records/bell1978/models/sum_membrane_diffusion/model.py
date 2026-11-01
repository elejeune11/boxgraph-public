def run(inputs, settings):
    return {"Dm_sum": inputs["DmA"] + inputs["DmB"]}


def symbolic():
    import sympy as sp
    DmA, DmB = sp.symbols("DmA DmB", positive=True)
    return {"Dm_sum": DmA + DmB}
