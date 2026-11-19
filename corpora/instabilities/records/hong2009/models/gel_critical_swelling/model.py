def run(inputs, settings):
    # Eq. 5/6 in generalized plane strain: lambda_3/lambda_1 = 1/(1 - eps)^2;
    # the bonded gel has lambda_3/lambda_1 = eta^(2/3)/eta^(-1/3) = eta.
    return {"eta": 1 / (1 - inputs["eps"]) ** 2}


def symbolic():
    import sympy as sp
    eps = sp.symbols("eps", positive=True)
    return {"eta": 1 / (1 - eps) ** 2}
