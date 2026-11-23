# Eq. 9: nc = n*c nc,free/nc,tot (no rounding to an integer is printed).


def run(inputs, settings):
    return {"nc": inputs["nc_max"] * inputs["nc_free"] / inputs["nc_tot"]}


def symbolic():
    import sympy as sp
    nc_max, nc_free, nc_tot = sp.symbols("nc_max nc_free nc_tot", positive=True)
    return {"nc": nc_max * nc_free / nc_tot}
