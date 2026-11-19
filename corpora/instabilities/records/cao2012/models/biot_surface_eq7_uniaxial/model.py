# Eq. 7, eW = 1 - c/sqrt(lambda_3), with the uniaxial-stress state lambda_2 = lambda_3 =
# 1/sqrt(lambda_1) (Sec. 3.3) and lambda_1 = 1 - eW (Eq. 4):
# lambda_1 = c lambda_1^(1/4)  =>  lambda_1 = c^(4/3).


def run(inputs, settings):
    return {"eW": 1 - inputs["c"] ** (4 / 3)}


def symbolic():
    import sympy as sp
    c = sp.symbols("c", positive=True)
    return {"eW": 1 - c ** sp.Rational(4, 3)}
