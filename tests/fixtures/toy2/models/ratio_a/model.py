def run(i, s):
    return {'tau': 1 / i['k0']}
def symbolic():
    import sympy as sp
    return {'tau': 1 / sp.Symbol('k0', positive=True)}
