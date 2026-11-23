# The mean of the binned values of a frequency histogram: sum of bin centre x fraction / sum of
# fractions. It differs from the mean of the raw values by up to about half a bin width.


def run(inputs, settings):
    h = inputs["h"]
    return {"mean": sum(x * f for x, f in zip(h["x"], h["y"])) / sum(h["y"])}
