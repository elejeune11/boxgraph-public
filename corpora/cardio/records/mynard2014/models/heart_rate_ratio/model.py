def run(inputs, settings):
    return {"ratio": inputs["HR_n"] / inputs["HR_a"]}


def symbolic():
    import sympy as sp
    HR_n, HR_a = sp.symbols("HR_n HR_a", positive=True)
    return {"ratio": HR_n / HR_a}
