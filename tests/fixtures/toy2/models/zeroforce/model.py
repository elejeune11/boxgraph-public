def run(i, s):
    return {'tau': 1 / i['k0']}
def symbolic():
    import sympy as sp
    k0 = sp.symbols('k0', positive=True)
    return {'tau': 1 / k0}
