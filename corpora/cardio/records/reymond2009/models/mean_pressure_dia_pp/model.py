# p. 7: mean sphygmomanometer pressure Pmean ~= Pdiastole + PP/3, all in mmHg.


def run(inputs, settings):
    return {"Pmean": inputs["Pdiastole"] + inputs["PP"] / 3.0}


def symbolic():
    import sympy as sp
    Pdiastole, PP = sp.symbols("Pdiastole PP", positive=True)
    return {"Pmean": Pdiastole + PP / 3}
