# Eq. 9 (p. 5) averaged over one period of a periodic solution: the time derivatives average to zero,
# leaving P = Pout + Q (R1 + R2) for the flow Q into one Windkessel. With n identical terminals in
# parallel each takes Q/n. The pressure loss along the 1D vessel(s) upstream is neglected (reader's choice).


def run(inputs, settings):
    q = inputs["Q"] / inputs["n"]
    return {"P": inputs["Pout"] + q * (inputs["R1"] + inputs["R2"])}


def symbolic():
    import sympy as sp
    Q, n, R1, R2, Pout = sp.symbols("Q n R1 R2 Pout", positive=True)
    return {"P": Pout + Q / n * (R1 + R2)}
