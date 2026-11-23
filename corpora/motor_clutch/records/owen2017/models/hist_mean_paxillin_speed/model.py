# Mean of a binned distribution: sum(x_i n_i) / sum(n_i) over the bins of a plotted histogram,
# each bin at its centre. Bins read as empty (n = 0) add nothing.


def run(inputs, settings):
    x, n = inputs["n"]["x"], inputs["n"]["y"]
    total = sum(n)
    return {"mean": sum(a * b for a, b in zip(x, n)) / total}
