# Eq. 2: vm,j = v*m (1 - κs xs,j / (nm,j Fm)). Units: nm/s, pN/nm, nm, pN. No clamp: as printed.


def run(inputs, settings):
    load = inputs["ks"] * inputs["xs"]
    return {"vm_j": inputs["vm"] * (1.0 - load / (inputs["nm"] * inputs["Fm"]))}


def symbolic():
    import sympy as sp
    vm, ks, xs, nm, Fm = sp.symbols("vm ks xs nm Fm", positive=True)
    return {"vm_j": vm * (1 - ks * xs / (nm * Fm))}
