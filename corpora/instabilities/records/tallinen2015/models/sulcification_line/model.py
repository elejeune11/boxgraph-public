# The dashed vertical line 'Sulcification' (gs) of Fig. 3: on axes (g, A/h) it is the line
# g = gs = 1/lambda_s for every amplitude. The amplitude input only says where on the line the value
# is read; it does not enter the result.


def run(inputs, settings):
    return {"g": 1.0 / inputs["lam_s"]}


def symbolic():
    import sympy as sp
    lam_s, A = sp.symbols("lam_s A", positive=True)
    return {"g": 1 / lam_s}
