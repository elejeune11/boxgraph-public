def run(i, s):
    return {'tau': 1 / i['r']}
def symbolic():
    import sympy as sp
    return {'tau': 1 / sp.Symbol('r', positive=True)}
