def run(inputs, settings):
    return {"pct": 100.0 * inputs["sd"] / inputs["mean"]}


def symbolic():
    import sympy as sp
    sd, mean = sp.symbols("sd mean", positive=True)
    return {"pct": 100 * sd / mean}
