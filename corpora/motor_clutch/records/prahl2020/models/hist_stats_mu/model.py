# Histogram statistics from the bars of a histogram: the number of entries (sum of the counts) and
# the mean of the binned values (sum of bin centre x count / sum of counts). The binned mean
# differs from the mean of the raw values by up to about half a bin width.


def run(inputs, settings):
    h = inputs["h"]
    xs, ns = h["x"], h["y"]
    total = sum(ns)
    return {"n": total, "mean": sum(x * n for x, n in zip(xs, ns)) / total}
