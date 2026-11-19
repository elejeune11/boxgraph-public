def run(inputs, settings):
    # Plane strain in the intermediate state of Fig. 4: lambda_1' = 1 - eps, lambda_3' = 1/lambda_1'.
    # Eq. 3: lambda_1 = lambda_1'/sqrt(lambda_2), lambda_3 = lambda_3'/sqrt(lambda_2), so
    # lambda_3/lambda_1 = lambda_3'/lambda_1' = 1/lambda_1'^2, for any lambda_2.
    lam1p = 1 - inputs["eps"]
    return {"ratio": 1 / lam1p**2}


def symbolic():
    import sympy as sp
    eps = sp.symbols("eps", positive=True)
    return {"ratio": 1 / (1 - eps) ** 2}
