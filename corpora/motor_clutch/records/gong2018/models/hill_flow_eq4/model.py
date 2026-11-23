# Vf = vu (1 - Fs/(Nm Fm)) (Eq. 4).  Ports: vu nm/s, Fs pN, Nm dimensionless, Fm pN -> Vf nm/s.
def run(inputs, settings):
    return {"Vf": inputs["vu"] * (1.0 - inputs["Fs"] / (inputs["Nm"] * inputs["Fm"]))}


def symbolic():
    import sympy as sp
    vu, Fs, Nm, Fm = sp.symbols("vu Fs Nm Fm", positive=True)
    return {"Vf": vu * (1 - Fs / (Nm * Fm))}
