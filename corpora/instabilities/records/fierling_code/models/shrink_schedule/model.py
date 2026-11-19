# Port of the pre-strain loop 'myosin': ratio_shrink := ratio_shrink/q once per step, frame n after n - 1 steps.


def run(inputs, settings):
    return {"gamma": inputs["q"] ** (-(round(inputs["n"]) - 1))}
