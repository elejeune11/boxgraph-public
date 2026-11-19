# Arithmetic mean of the y values of a curve (here: one column of Table 1, one value per species).


def run(inputs, settings):
    y = inputs["d"]["y"]
    return {"mean": sum(y) / len(y)}
