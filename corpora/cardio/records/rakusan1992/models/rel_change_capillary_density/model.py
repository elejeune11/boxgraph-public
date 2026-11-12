# Relative change of a group mean from a reference group mean, in percent.


def run(inputs, settings):
    d = 100.0 * (inputs["val"] - inputs["ref"]) / inputs["ref"]
    return {"diff": d, "decrease": -d}


def symbolic():
    import sympy as sp
    val, ref = sp.symbols("val ref", positive=True)
    d = 100 * (val - ref) / ref
    return {"diff": d, "decrease": -d}
