def run(inputs, settings):
    v_retro = inputs["vu"] * (1.0 - inputs["F_sum"] / inputs["Fstall"])
    return {"v_retrograde": v_retro, "v_spread": inputs["vu"] - v_retro}


def symbolic():
    import sympy as sp
    vu, F_sum, Fstall = sp.symbols("vu F_sum Fstall", positive=True)
    v_retro = vu * (1 - F_sum / Fstall)
    return {"v_retrograde": v_retro, "v_spread": vu - v_retro}
