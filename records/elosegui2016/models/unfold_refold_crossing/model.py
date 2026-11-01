# Force on talin at which the slip-bond unfolding rate equals the refolding rate:
# ln_kunf0 + kunf_b f = ln_kfold0 + kfold_b f. Our code.


def run(inputs, settings):
    f = (inputs["ln_kfold0"] - inputs["ln_kunf0"]) / (inputs["kunf_b"] - inputs["kfold_b"])
    return {"f_cross": f}


def symbolic():
    import sympy as sp
    a, b, c, d = sp.symbols("ln_kunf0 kunf_b ln_kfold0 kfold_b")
    return {"f_cross": (c - a) / (b - d)}
