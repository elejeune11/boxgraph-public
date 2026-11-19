def run(inputs, settings):
    return {"eps_c": inputs["Nc_over_hE"] / (1 + inputs["nu"])}


def symbolic():
    import sympy as sp
    n, nu = sp.symbols("Nc_over_hE nu", positive=True)
    return {"eps_c": n / (1 + nu)}
