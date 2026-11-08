# Eq. T5 with the pericardial cavity volume of p. 8 (all volumes in mL, pressure in mmHg).
import math


def run(inputs, settings):
    vpc = (inputs["v_lv"] + inputs["v_rv"] + inputs["v_la"] + inputs["v_ra"]
           + inputs["v_pcf"] + inputs["v_myo"])
    return {"ppc": inputs["Kpc"] * math.exp((vpc - inputs["V0pc"]) / inputs["Phi"])}


def symbolic():
    import sympy as sp
    Kpc, V0pc, Phi, v_lv, v_rv, v_la, v_ra, v_pcf, v_myo = sp.symbols(
        "Kpc V0pc Phi v_lv v_rv v_la v_ra v_pcf v_myo", positive=True)
    vpc = v_lv + v_rv + v_la + v_ra + v_pcf + v_myo
    return {"ppc": Kpc * sp.exp((vpc - V0pc) / Phi)}
