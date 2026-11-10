# Acceleration factor: the build time reported elsewhere divided by the build time of the presented code
# (p. 3, "a median of 15 min, compared with 59.96 hours reported elsewhere"). Times in s.
def run(inputs, settings):
    return {"factor": inputs["t_ref"] / inputs["t_new"]}


def symbolic():
    import sympy as sp

    t_ref, t_new = sp.symbols("t_ref t_new", positive=True)
    return {"factor": t_ref / t_new}
