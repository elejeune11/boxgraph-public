# Mean area of the domains that tile a section: one domain per capillary.


def run(inputs, settings):
    return {"A": 1e6 / inputs["CD"]}  # 1/mm^2 -> um^2 per capillary


def symbolic():
    import sympy as sp
    CD = sp.symbols("CD", positive=True)
    return {"A": 10**6 / CD}
