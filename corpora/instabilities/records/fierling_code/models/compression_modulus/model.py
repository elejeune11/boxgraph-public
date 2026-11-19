# Port of settings.plot line 7 (chi=Y/2/(1-nu)), written with kappa and R so the nondimensionalisation is explicit.


def run(inputs, settings):
    Y, nu, kappa, R = inputs["Y"], inputs["nu"], inputs["kappa"], inputs["R"]
    return {"chi": Y * R**2 / (2 * (1 - nu) * kappa)}


def symbolic():
    import sympy as sp
    Y, kappa, R = sp.symbols("Y kappa R", positive=True)
    nu = sp.Symbol("nu")
    return {"chi": Y * R**2 / (2 * (1 - nu) * kappa)}
