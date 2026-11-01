# p. 9, in words: the number of motors that together stall at a traction force F, each stalling at Fm.
# n = F / Fm. F and Fm in pN.


def run(inputs, settings):
    return {"n": inputs["F"] / inputs["Fm"]}


def symbolic():
    import sympy as sp
    F, Fm = sp.symbols("F Fm", positive=True)
    return {"n": F / Fm}
