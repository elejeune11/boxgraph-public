# Share of each of the six waves in their summed cumulative intensity, in percent. Applied to group means
# this is a ratio of means; the paper averaged per-subject proportions (see the record's questions).


def run(inputs, settings):
    keys = ["I1", "I2", "I3", "I4", "I5", "I6"]
    total = sum(inputs[k] for k in keys)
    return {f"p{i + 1}": 100.0 * inputs[k] / total for i, k in enumerate(keys)}


def symbolic():
    import sympy as sp
    I = sp.symbols("I1 I2 I3 I4 I5 I6", positive=True)
    total = sum(I)
    return {f"p{i + 1}": 100 * I[i] / total for i in range(6)}
