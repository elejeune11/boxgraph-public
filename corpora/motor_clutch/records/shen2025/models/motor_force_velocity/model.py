# Piecewise linear force-velocity relation of one attached myosin motor (p. 2), as printed.
def run(inputs, settings):
    vu, fl, fs, vb = inputs["vu"], inputs["fl"], inputs["fs"], inputs["vb"]
    if fl <= 0:
        return {"vm": vu}
    if fl <= fs:
        return {"vm": vu * (1.0 - fl / fs)}
    return {"vm": vb}
