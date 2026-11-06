def run(inputs, settings):
    b1 = inputs["beta1"]
    a = 1 - 32 / b1**4
    return {"lambda_q": 1 / b1**2, "lambda_p": a / b1**2}


def symbolic():
    import sympy as sp
    b1 = sp.symbols("beta1", positive=True)
    return {"lambda_q": 1 / b1**2, "lambda_p": (1 - 32 / b1**4) / b1**2}
