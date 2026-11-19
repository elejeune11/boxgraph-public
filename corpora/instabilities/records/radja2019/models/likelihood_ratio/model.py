# The usual likelihood-ratio statistic, twice the difference of the log-likelihoods.
# The paper names the statistic and prints its values (Table S4) but not the formula.


def run(inputs, settings):
    return {"LR": 2.0 * (inputs["nll_simple"] - inputs["nll_complex"])}


def symbolic():
    import sympy as sp
    a, b = sp.symbols("nll_simple nll_complex")
    return {"LR": 2 * (a - b)}
