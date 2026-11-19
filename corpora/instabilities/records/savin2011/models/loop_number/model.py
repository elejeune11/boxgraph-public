# Fig. 3a: Lt/n = lambda, so n = Lt/lambda. Both lengths in mm.


def run(inputs, settings):
    return {"n": inputs["Lt"] / inputs["lam"]}


def symbolic():
    import sympy as sp
    Lt, lam = sp.symbols("Lt lam", positive=True)
    return {"n": Lt / lam}
