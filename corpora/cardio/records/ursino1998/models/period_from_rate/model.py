# Heart period from heart rate, T = 1/HR (p. 4 and p. 10, "HR = 1/T"). HR in 1/s, T in s.
def run(inputs, settings):
    return {"T": 1.0 / inputs["HR"]}


def symbolic():
    import sympy as sp
    hr = sp.symbols("HR", positive=True)
    return {"T": 1 / hr}
