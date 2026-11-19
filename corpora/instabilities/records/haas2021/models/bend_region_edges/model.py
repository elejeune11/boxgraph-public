# The bend region of Fig. 4(g) as the caption of Fig. 5(b) states it: s0 - w < s < s0. The band is
# drawn across the whole panel, so its edges do not depend on the level of the plotted strain, which
# is an input only so that the edges can be compared at the levels where they were read.


def run(inputs, settings):
    return {"s_start": inputs["s0"] - inputs["w"], "s_end": inputs["s0"]}


def symbolic():
    import sympy as sp
    s0, w = sp.symbols("s0 w", positive=True)
    return {"s_start": s0 - w, "s_end": s0}
