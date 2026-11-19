def run(inputs, settings):
    sigma = inputs["Em"] * (inputs["alpha_p"] - inputs["alpha_m"]) * (inputs["TD"] - inputs["T"]) / (1 - inputs["nu_m"])
    return {"sigma_o": sigma}


def symbolic():
    import sympy as sp
    Em, nu_m, alpha_p, alpha_m, TD, T = sp.symbols("Em nu_m alpha_p alpha_m TD T", real=True)
    return {"sigma_o": Em * (alpha_p - alpha_m) * (TD - T) / (1 - nu_m)}
