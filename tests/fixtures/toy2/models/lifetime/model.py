import math
def run(i, s):
    return {'tau': i['tau0'] * math.exp(-i['f'] / i['fb'])}
def symbolic():
    import sympy as sp
    tau0, f, fb = sp.symbols('tau0 f fb', positive=True)
    return {'tau': tau0 * sp.exp(-f / fb)}
