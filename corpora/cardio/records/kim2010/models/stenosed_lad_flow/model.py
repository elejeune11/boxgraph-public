MMHG_DYN_CM2 = 1333.22387415  # 1 mmHg in dyn/cm^2


def run(inputs, settings):
    qc = inputs["Ra_c"] + inputs["Ram_c"] + inputs["Rv_c"]
    qd = inputs["Ra_d"] + inputs["Ram_d"] + inputs["Rv_d"]
    dp = (inputs["P"] - inputs["Pv"]) * MMHG_DYN_CM2           # dyn/cm^2
    return {"Q": dp * (1.0 / qc + 1.0 / qd) / 1000.0}          # kdyn*s/cm^5 -> dyn*s/cm^5: x 1000


def symbolic():
    import sympy as sp
    P, Pv, a, b, c, d, e, f = sp.symbols("P Pv Ra_c Ram_c Rv_c Ra_d Ram_d Rv_d", positive=True)
    return {"Q": (P - Pv) * MMHG_DYN_CM2 * (1 / (a + b + c) + 1 / (d + e + f)) / 1000}
