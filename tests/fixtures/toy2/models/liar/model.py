def run(i, s):
    return {'tau': 2 / i['k0']}  # the code doubles it


def symbolic():
    import sympy as sp
    k0 = sp.symbols('k0', positive=True)
    return {'tau': 1 / k0}  # the written form does not
