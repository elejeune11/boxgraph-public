# The value of the plotted point whose x is nearest the setting x0 (within half a group spacing).


def run(inputs, settings):
    c = inputs["R"]
    x0 = float(settings["x0"])
    i = min(range(len(c["x"])), key=lambda k: abs(c["x"][k] - x0))
    if abs(c["x"][i] - x0) > 0.25:
        raise ValueError("no plotted point near x0")
    return {"R0": c["y"][i]}
