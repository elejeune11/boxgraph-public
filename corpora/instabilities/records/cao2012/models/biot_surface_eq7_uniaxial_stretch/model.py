# Eq. 7, lambda_1 = c/sqrt(lambda_3) (with Eq. 4), and the uniaxial-stress state lambda_3 = 1/sqrt(lambda_1):
# lambda_1 = c lambda_1^(1/4)  =>  lambda_1 = c^(4/3).


def run(inputs, settings):
    return {"lam1": inputs["c"] ** (4 / 3)}


def symbolic():
    import sympy as sp
    c = sp.symbols("c", positive=True)
    return {"lam1": c ** sp.Rational(4, 3)}
