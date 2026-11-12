# Blood volume per tissue volume: c [mL/g] x rho [g/mL] -> mL/mL; the microvascular part takes s [percent].


def run(inputs, settings):
    phi = inputs["c"] * inputs["rho"]
    return {"phi": phi, "phi_micro": inputs["s"] / 100.0 * phi}


def symbolic():
    import sympy as sp
    c, s, rho = sp.symbols("c s rho", positive=True)
    return {"phi": c * rho, "phi_micro": s / 100 * c * rho}
