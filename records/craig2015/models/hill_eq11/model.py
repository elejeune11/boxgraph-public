def run(inputs, settings):
    F = inputs["Ftot"]
    return {"VLM": inputs["Vmax"] * F / (inputs["Fk"] + F)}


def symbolic():
    import sympy as sp
    Vmax, Fk, Ftot = sp.symbols("Vmax Fk Ftot", positive=True)
    return {"VLM": Vmax * Ftot / (Fk + Ftot)}
