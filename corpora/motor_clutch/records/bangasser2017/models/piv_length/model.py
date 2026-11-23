def run(inputs, settings):
    return {"L": inputs["npx"] * inputs["pixel"]}


def symbolic():
    import sympy as sp
    npx, pixel = sp.symbols("npx pixel", positive=True)
    return {"L": npx * pixel}
