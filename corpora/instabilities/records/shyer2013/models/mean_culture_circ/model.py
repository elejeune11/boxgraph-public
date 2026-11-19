"""Mean of a bar chart's ratios over the drug conditions, the control category left out."""


def run(inputs, settings):
    c = settings["control_x"]
    ys = [y for x, y in zip(inputs["r"]["x"], inputs["r"]["y"]) if y is not None and abs(x - c) > 0.5]
    return {"r_mean": sum(ys) / len(ys)}
