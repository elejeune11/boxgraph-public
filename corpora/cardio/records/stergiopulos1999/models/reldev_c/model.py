"""Relative deviation of an estimate from the actual value, in percent."""


def run(inputs, settings):
    r = (inputs["est"] - inputs["act"]) / inputs["act"] * 100.0
    return {"over": r, "under": -r, "mag": abs(r)}
