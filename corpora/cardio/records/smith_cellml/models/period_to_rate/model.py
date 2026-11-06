# Heart rate in beats per minute from the period in seconds.


def run(inputs, settings):
    return {"HR": 60.0 / inputs["period"]}


def symbolic():
    import sympy as sp
    period = sp.symbols("period", positive=True)
    return {"HR": 60 / period}
