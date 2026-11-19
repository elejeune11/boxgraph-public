# The arithmetic mean of every plotted e_c (each sample counts once).


def run(inputs, settings):
    ys = inputs["ec"]["y"]
    return {"ec_mean": sum(ys) / len(ys)}
