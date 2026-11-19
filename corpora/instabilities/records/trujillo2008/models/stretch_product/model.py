# lambda1^2 lambda3, the in-plane stretch product of Biot's condition as the paper writes it (p. 2).


def run(inputs, settings):
    return {"lam_prod": inputs["lam1"] ** 2 * inputs["lam3"]}


def symbolic():
    import sympy as sp
    lam1, lam3 = sp.symbols("lam1 lam3", positive=True)
    return {"lam_prod": lam1**2 * lam3}
