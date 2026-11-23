# Port of Cell1DPublish.cpp line 405, as written, including the clip at zero speed.


def run(inputs, settings):
    load = inputs["F"] / (inputs["nm"] * inputs["nmFactor"] * inputs["Fm"])
    return {"vflow": max(0.0, inputs["vu"] * (1.0 - load))}
