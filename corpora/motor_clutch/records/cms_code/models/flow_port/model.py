# Port of cms2Dv1_0.m lines 200-202 (our code): vf = vu*(1 - Ksub*sdisp/(nm*Fm)), set to 0 if negative.


def run(inputs, settings):
    vf = inputs["vu"] * (1 - (inputs["Ksub"] * abs(inputs["sdisp"])) / (inputs["nm"] * inputs["Fm"]))
    if vf < 0:
        vf = 0.0
    return {"vf": vf}
