# Sum of the regional compliances of Table 3 (mL/mmHg); the liver is inside the systemic veins.


def run(inputs, settings):
    return {"C_total": inputs["C_sa"] + inputs["C_sv"] + inputs["C_pa"] + inputs["C_pv"]}


def symbolic():
    import sympy as sp
    C_sa, C_sv, C_pa, C_pv = sp.symbols("C_sa C_sv C_pa C_pv", positive=True)
    return {"C_total": C_sa + C_sv + C_pa + C_pv}
