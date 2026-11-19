# Arithmetic mean of the values read from the figure (one per plotted point).


def run(inputs, settings):
    y = inputs["k"]["y"]
    return {"mean": sum(y) / len(y), "n": float(len(y))}
