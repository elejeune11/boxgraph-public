# gs = 1/lambda_s (p. 2): uniaxial growth g of the layer is equivalent to a compressive stretch 1/g.


def run(inputs, settings):
    return {"gs": 1.0 / inputs["lam_s"]}


def symbolic():
    import sympy as sp
    lam_s = sp.symbols("lam_s", positive=True)
    return {"gs": 1 / lam_s}
