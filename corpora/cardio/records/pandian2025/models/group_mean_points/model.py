# Mean of the dots of each group; a dot's group is the integer part of its x (1.01 ... -> 1). nm/s in and out.
import math


def run(inputs, settings):
    groups = {}
    for x, y in zip(inputs["P"]["x"], inputs["P"]["y"]):
        groups.setdefault(int(math.floor(x + 1e-9)), []).append(y)
    xs = sorted(groups)
    return {"Pm": {"x": [float(k) for k in xs], "y": [sum(groups[k]) / len(groups[k]) for k in xs]}}
