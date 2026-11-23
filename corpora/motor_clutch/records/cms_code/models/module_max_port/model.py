# Port of cms2Dv1_0.m lines 39-40 (our code): maxm = mpool*0.1, maxc = cpool*0.1.


def run(inputs, settings):
    return {"maxm": inputs["mpool"] * inputs["fm"], "maxc": inputs["cpool"] * inputs["fc"]}


def symbolic():
    import sympy as sp
    mpool, cpool, fm, fc = sp.symbols("mpool cpool fm fc", positive=True)
    return {"maxm": mpool * fm, "maxc": cpool * fc}
