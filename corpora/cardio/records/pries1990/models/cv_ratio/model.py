# Coefficient of variation: standard deviation over mean.


def run(inputs, settings):
    return {"cv": inputs["sd"] / inputs["mean"]}


def symbolic():
    import sympy as sp
    mean, sd = sp.symbols("mean sd", positive=True)
    return {"cv": sd / mean}
