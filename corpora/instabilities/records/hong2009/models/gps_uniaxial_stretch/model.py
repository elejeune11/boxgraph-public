def run(inputs, settings):
    # lambda_3/lambda_1 = 1/(1 - eps)^2 (Eqs. 3, 5, 6); uniaxial: lambda_2 = lambda_3 = lambda_1^(-1/2)
    # so lambda_1^(-3/2) = (1 - eps)^(-2)  ->  lambda_1 = (1 - eps)^(4/3)
    return {"lam1": (1 - inputs["eps"]) ** (4.0 / 3.0)}


def symbolic():
    import sympy as sp
    eps = sp.symbols("eps", positive=True)
    return {"lam1": (1 - eps) ** sp.Rational(4, 3)}
