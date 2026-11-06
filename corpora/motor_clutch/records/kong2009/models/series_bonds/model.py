# Two bonds in series under the same force, each dissociating at its own first-order rate: the chain
# breaks at the sum of the rates (p. 3), so its mean lifetime is the inverse of the summed inverse lifetimes.


def run(inputs, settings):
    return {"tau_serial": 1.0 / (1.0 / inputs["tau_1"] + 1.0 / inputs["tau_2"])}


def symbolic():
    import sympy as sp

    tau_1, tau_2 = sp.symbols("tau_1 tau_2", positive=True)
    return {"tau_serial": 1 / (1 / tau_1 + 1 / tau_2)}
