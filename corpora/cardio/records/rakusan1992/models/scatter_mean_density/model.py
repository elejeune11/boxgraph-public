# Means over the per-heart markers of one group in a scatter of capillary density (1/mm^2) against
# heart mass (g): the arithmetic mean of y and of x.


def run(inputs, settings):
    x, y = inputs["P"]["x"], inputs["P"]["y"]
    return {"y_mean": sum(y) / len(y), "x_mean": sum(x) / len(x)}
