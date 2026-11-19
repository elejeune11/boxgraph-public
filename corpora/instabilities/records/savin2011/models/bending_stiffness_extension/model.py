# SI p. 6: the slope of the straight tube "yields a stiffness of order 4 Et It/(ro^2 + ri^2)",
# taken as an equality: Et It = (dF/d eps)(ro^2 + ri^2)/4. slope in N, radii in um; Et It in N m^2.


def run(inputs, settings):
    ro, ri = inputs["ro"] * 1e-6, inputs["ri"] * 1e-6
    return {"EtIt": inputs["slope"] * (ro ** 2 + ri ** 2) / 4}


def symbolic():
    import sympy as sp
    slope, ro, ri = sp.symbols("slope ro ri", positive=True)
    return {"EtIt": slope * ((ro / 10**6) ** 2 + (ri / 10**6) ** 2) / 4}
