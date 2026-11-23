# Step 5 of the Supporting Material algorithm: linear force-velocity relation of the motors,
# v_f = vu (1 - ksub xsub/(nm Fm)), as motor_clutch_ssa uses it. Units nm/s, pN/nm, nm, pN.
def run(inputs, settings):
    load = inputs["ksub"] * inputs["xsub"]
    return {"v_f": inputs["vu"] * (1.0 - load / (inputs["nm"] * inputs["Fm"]))}


def symbolic():
    import sympy as sp
    vu, ksub, xsub, nm, Fm = sp.symbols("vu ksub xsub nm Fm", positive=True)
    return {"v_f": vu * (1 - ksub * xsub / (nm * Fm))}
