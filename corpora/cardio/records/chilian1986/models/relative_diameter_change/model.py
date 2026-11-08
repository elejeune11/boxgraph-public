# Applied to the group means (mean |change| over mean control diameter); the paper averages
# per-vessel percentages, so the two need not agree exactly.


def run(inputs, settings):
    return {"rel": 100.0 * inputs["dd"] / inputs["d0"]}


def symbolic():
    import sympy as sp
    dd, d0 = sp.symbols("dd d0", positive=True)
    return {"rel": 100 * dd / d0}
