import math


def run(inputs, settings):
    th = math.radians(inputs["theta"])
    tm = math.radians(inputs["theta_max"])
    return {"AR": 100.0 * (1.0 - math.cos(th)) ** 2 / (1.0 - math.cos(tm)) ** 2}


def symbolic():
    import sympy as sp
    theta, theta_max = sp.symbols("theta theta_max", positive=True)
    return {"AR": 100 * (1 - sp.cos(theta * sp.pi / 180)) ** 2 / (1 - sp.cos(theta_max * sp.pi / 180)) ** 2}
