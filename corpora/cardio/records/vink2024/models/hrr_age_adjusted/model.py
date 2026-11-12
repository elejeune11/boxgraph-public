# Age-adjusted heart rate reserve, 100 (HRmax - HRrest) / (f (220 - age) - HRrest).
# Heart rates in 1/min (beats per minute), age in years; 220 is in beats per minute with age in years.


def run(inputs, settings):
    pred = inputs["f"] * (220.0 - inputs["age"])
    return {"HRRadj": 100.0 * (inputs["HRmax"] - inputs["HRrest"]) / (pred - inputs["HRrest"])}


def symbolic():
    import sympy as sp
    HRmax, HRrest, age, f = sp.symbols("HRmax HRrest age f", positive=True)
    return {"HRRadj": 100 * (HRmax - HRrest) / (f * (220 - age) - HRrest)}
