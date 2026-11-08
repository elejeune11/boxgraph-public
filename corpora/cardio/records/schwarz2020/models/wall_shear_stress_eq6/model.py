def run(inputs, settings):
    return {"tau": inputs["dP"] * inputs["d"] / (4 * inputs["l"])}


def symbolic():
    import sympy as sp
    dP, d, l = sp.symbols("dP d l", positive=True)
    return {"tau": dP * d / (4 * l)}
