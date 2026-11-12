# Count, mean and sample SD of a histogram given as bar heights at the bin midpoints (x in um).
# Bar heights are numbers of segments, so each is rounded to a whole number. The mean and SD place every
# segment at its bin midpoint, an approximation of the statistics of the unbinned lengths.
import math


def run(inputs, settings):
    x = [float(v) for v in inputs["H"]["x"]]
    c = [float(round(v)) for v in inputs["H"]["y"]]
    n = sum(c)
    mean = sum(ci * xi for ci, xi in zip(c, x)) / n
    var = sum(ci * (xi - mean) ** 2 for ci, xi in zip(c, x)) / (n - 1)
    return {"n": n, "mean": mean, "sd": math.sqrt(var)}
