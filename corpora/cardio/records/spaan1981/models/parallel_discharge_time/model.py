def run(inputs, settings):
    ra, rv = inputs["Ra"], inputs["Rv"]
    return {"tau": inputs["Cim"] * ra * rv / (ra + rv)}


def symbolic():
    import sympy as sp
    Cim, Ra, Rv = sp.symbols("Cim Ra Rv", positive=True)
    return {"tau": Cim * Ra * Rv / (Ra + Rv)}
