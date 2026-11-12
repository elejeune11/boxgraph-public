# Ratio of two group mean heart weights.


def run(inputs, settings):
    return {"ratio": inputs["val"] / inputs["ref"]}


def symbolic():
    import sympy as sp
    val, ref = sp.symbols("val ref", positive=True)
    return {"ratio": val / ref}
