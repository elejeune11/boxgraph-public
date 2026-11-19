# SI p. 3: F(d) = F0 (d0/d)^alpha. Distances in mm, forces in N.


def run(inputs, settings):
    return {"F": inputs["F0"] * (inputs["d0"] / inputs["d"]) ** inputs["alpha"]}


def symbolic():
    import sympy as sp
    F0, alpha, d0, d = sp.symbols("F0 alpha d0 d", positive=True)
    return {"F": F0 * (d0 / d) ** alpha}
