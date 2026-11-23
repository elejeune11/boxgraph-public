# Linear force-velocity relation of the motors (SOM Eqs. 3-4), as one step of the motor-clutch simulation.
def run(inputs, settings):
    Fstall = inputs["nm"] * inputs["Fm"]                                  # Eq. 4
    return {"vfilament": inputs["vu"] * (1.0 - inputs["ksub"] * inputs["xsub"] / Fstall)}   # Eq. 3


def symbolic():
    import sympy as sp
    vu, ksub, xsub, nm, Fm = sp.symbols("vu ksub xsub nm Fm", positive=True)
    return {"vfilament": vu * (1 - ksub * xsub / (nm * Fm))}
