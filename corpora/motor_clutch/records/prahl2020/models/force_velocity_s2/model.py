def run(inputs, settings):
    load = inputs["ksub"] * inputs["dxsub"] / (inputs["Fmotor"] * inputs["nmotor_j"])
    return {"vflow": inputs["vmotor"] * (1.0 - load)}


def symbolic():
    import sympy as sp
    vmotor, ksub, dxsub, Fmotor, nmotor_j = sp.symbols("vmotor ksub dxsub Fmotor nmotor_j", positive=True)
    return {"vflow": vmotor * (1 - ksub * dxsub / (Fmotor * nmotor_j))}
