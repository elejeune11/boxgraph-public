# The flat part of the blue threshold curve of Fig. 4(b) (eta < eta_s): the sulcification threshold for
# equibiaxial growth, g^(3/2) = gs = 1/lambda_s (p. 4), the same for every eta. The eta input only says
# where on the line the value is read; it does not enter the result.


def run(inputs, settings):
    return {"g": (1.0 / inputs["lam_s"]) ** (2.0 / 3.0)}


def symbolic():
    import sympy as sp
    lam_s, eta = sp.symbols("lam_s eta", positive=True)
    return {"g": (1 / lam_s) ** sp.Rational(2, 3)}
