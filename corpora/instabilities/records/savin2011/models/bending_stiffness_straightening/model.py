# SI p. 6: F = (Et It/v0^2) delta in the straightening regime, so Et It = (dF/d delta) v0^2.
# slope in N, ro in um (-> m); Et It in N m^2.


def run(inputs, settings):
    v0 = inputs["v0_over_ro"] * inputs["ro"] * 1e-6
    return {"EtIt": inputs["slope"] * v0 ** 2}


def symbolic():
    import sympy as sp
    slope, k, ro = sp.symbols("slope v0_over_ro ro", positive=True)
    return {"EtIt": slope * (k * ro * sp.Rational(1, 10**6)) ** 2}
