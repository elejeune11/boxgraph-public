def run(inputs, settings):
    k = 360.0 * inputs["td"]
    return {"k": k, "phase": k * inputs["f"]}


def symbolic():
    import sympy as sp
    td, f = sp.symbols("td f", positive=True)
    return {"k": 360 * td, "phase": 360 * td * f}
