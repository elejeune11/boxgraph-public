# Mean l0 of a vertical boundary line read at several u values.


def run(inputs, settings):
    y = [float(v) for v in inputs["L"]["y"]]
    return {"l0_b": sum(y) / len(y)}
