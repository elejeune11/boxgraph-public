# Eq. 8: nm = n*m nm,free/nm,tot (no rounding to an integer is printed).


def run(inputs, settings):
    return {"nm": inputs["nm_max"] * inputs["nm_free"] / inputs["nm_tot"]}


def symbolic():
    import sympy as sp
    nm_max, nm_free, nm_tot = sp.symbols("nm_max nm_free nm_tot", positive=True)
    return {"nm": nm_max * nm_free / nm_tot}
