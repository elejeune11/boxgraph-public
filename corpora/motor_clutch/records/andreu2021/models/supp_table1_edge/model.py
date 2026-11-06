# Supplementary Table 1 notes (i)-(ii): A = eps R, |v| = 2 A f, load = k A, loading rate = k |v|.
# Units: um, Hz, nN/um -> um, um/s, nN, nN/s.


def run(inputs, settings):
    A = inputs["eps"] * inputs["R"]
    v = 2.0 * A * inputs["f"]
    k = inputs["k"]
    return {"A": A, "v": v, "F": k * A, "Fdot": k * v}


def symbolic():
    import sympy as sp
    eps, R, f, k = sp.symbols("eps R f k", positive=True)
    A = eps * R
    return {"A": A, "v": 2 * A * f, "F": k * A, "Fdot": 2 * k * A * f}
