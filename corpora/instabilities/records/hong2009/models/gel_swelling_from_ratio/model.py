def run(inputs, settings):
    # lambda_3/lambda_1 = eta^(2/3) / eta^(-1/3) = eta
    return {"eta": inputs["ratio"]}


def symbolic():
    import sympy as sp
    ratio = sp.symbols("ratio", positive=True)
    return {"eta": ratio}
