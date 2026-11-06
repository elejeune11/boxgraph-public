def run(inputs, settings):
    return {
        "a_pulse": inputs["aS"] - inputs["aD"],
        "b_pulse": inputs["bS"] - inputs["bD"],
    }


def symbolic():
    import sympy as sp
    aS, bS, aD, bD = sp.symbols("aS bS aD bD", real=True)
    return {"a_pulse": aS - aD, "b_pulse": bS - bD}
