# The claim of switch_speed_claim, per perturbation condition (p. 5: "maximal stresses were always
# associated with a similar F-actin speed (Fig. 4, C and D, right)"): the speed at maximal
# traction is Vc whatever the condition. The condition is an input so that the claim can be run
# over the conditions of Fig. 4 D; it does not enter the result. Units: nm/s in and out.


def run(inputs, settings):
    return {"v_peak": inputs["v_c"]}


def symbolic():
    import sympy as sp
    v_c = sp.symbols("v_c", positive=True)
    return {"v_peak": v_c}
