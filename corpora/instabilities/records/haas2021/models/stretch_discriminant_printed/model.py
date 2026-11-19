# The closed form printed for the stretching discriminant: -48 (1 - eta^2)^-2.


def run(inputs, settings):
    eta = inputs["eta"]
    if not -1 < eta < 1:
        return {"D": None}
    return {"D": -48 * (1 - eta**2) ** -2}


def symbolic():
    import sympy as sp
    eta = sp.Symbol("eta", positive=True)
    return {"D": -48 * (1 - eta**2) ** -2}
