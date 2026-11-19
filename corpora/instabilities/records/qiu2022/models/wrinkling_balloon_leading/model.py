# Leading term of the balloon-limit wrinkling curvature printed on p. 3: kappa-hat_w = p-hat/2 + O(p-hat^2).


def run(inputs, settings):
    return {"khat_w": inputs["phat"] / 2}


def symbolic():
    import sympy as sp
    phat = sp.symbols("phat", positive=True)
    return {"khat_w": phat / 2}
