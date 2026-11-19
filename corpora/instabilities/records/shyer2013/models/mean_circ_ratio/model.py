"""Mean of a plotted ratio over all its plotted points."""


def run(inputs, settings):
    ys = [y for y in inputs["r"]["y"] if y is not None]
    return {"r_mean": sum(ys) / len(ys)}
