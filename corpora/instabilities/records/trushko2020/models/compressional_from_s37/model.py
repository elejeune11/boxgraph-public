def run(inputs, settings):
    r = 2.0 * (inputs["spring_ratio"] - 1.0) - inputs["bending_ratio"]
    return {"lambda_ratio": r, "lam": r * inputs["lambda_cap"]}


def symbolic():
    import sympy as sp
    s, b, lc = sp.symbols("spring_ratio bending_ratio lambda_cap", positive=True)
    r = 2 * (s - 1) - b
    return {"lambda_ratio": r, "lam": r * lc}
