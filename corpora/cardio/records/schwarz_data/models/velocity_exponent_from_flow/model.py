# Our own model: centerline velocity v = 8 Q/(pi d^2) segment by segment (Poiseuille flow), so a flow
# law Q ~ d^gamma implies v ~ d^(gamma - 2). Exactly so for a least-squares fit in log-log space
# (the log of v is the log of Q minus 2 log d plus a constant); not so for a non-linear fit.
def run(inputs, settings):
    return {"b_v": inputs["gamma"] - 2.0}


def symbolic():
    import sympy as sp
    gamma = sp.symbols("gamma")
    return {"b_v": gamma - 2}
