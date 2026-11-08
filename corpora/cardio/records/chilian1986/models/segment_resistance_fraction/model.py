# The partition of resistance (Methods) applied at two sites: the share between them is the
# difference of their distal shares, i.e. of their pressures as percentages of aortic pressure.


def run(inputs, settings):
    return {"segment": inputs["pct_up"] - inputs["pct_down"]}


def symbolic():
    import sympy as sp
    pct_up, pct_down = sp.symbols("pct_up pct_down", positive=True)
    return {"segment": pct_up - pct_down}
