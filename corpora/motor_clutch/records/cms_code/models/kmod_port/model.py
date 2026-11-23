# Port of cms2Dv1_0.m line 171 (our code): kmod = kmod0*(1-(factin/totact))^4.


def run(inputs, settings):
    return {"kmod": inputs["kmod0"] * (1 - inputs["factin"] / inputs["totact"]) ** 4}


def symbolic():
    import sympy as sp
    kmod0, factin, totact = sp.symbols("kmod0 factin totact", positive=True)
    return {"kmod": kmod0 * (1 - factin / totact) ** 4}
