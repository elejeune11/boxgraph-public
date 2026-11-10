# Kinematic viscosity from dynamic viscosity and density, nu = mu / rho (the relation between Table S3's
# rows mu, rho^f and nu). mu in cP (1 cP = 0.01 g/(cm s)), rho in g/cm^3, nu in cm^2/s.
def run(inputs, settings):
    return {"nu": inputs["mu"] / 100.0 / inputs["rho"]}


def symbolic():
    import sympy as sp

    mu, rho = sp.symbols("mu rho", positive=True)
    return {"nu": mu / 100 / rho}
