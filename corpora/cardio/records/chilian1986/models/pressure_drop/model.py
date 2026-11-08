def run(inputs, settings):
    return {"dP": inputs["Pa"] - inputs["Pm"]}


def symbolic():
    import sympy as sp
    Pa, Pm = sp.symbols("Pa Pm", positive=True)
    return {"dP": Pa - Pm}
