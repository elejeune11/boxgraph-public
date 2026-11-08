# Eq. 10 and Eq. 11 as printed, computed for n = top, top-1, ..., 1.
# The m = n term holds N'_n (and dN'_n) on both sides; it is solved for exactly:
#   N'_n (1 - C(n,n)) = C(n,n) N_n,cut + sum_(m>n) C(n,m)[N'_m + N_m,cut]
# A matrix component printed without an SE (a zero, or an exact count) has dC = 0.
PAIRS = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (5, 11), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 11), (7, 7), (7, 8), (7, 9), (7, 10), (7, 11), (8, 8), (8, 9), (8, 10), (8, 11), (9, 9), (9, 10), (9, 11), (10, 10), (10, 11), (11, 11)]
SE_PAIRS = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (7, 7), (7, 8), (7, 9), (7, 10), (8, 8), (8, 9), (8, 10), (9, 9), (9, 10), (10, 10)]


def run(inputs, settings):
    top = int(settings["top_order"])
    C = {(n, m): inputs[f"c_{n}_{m}"] for n, m in PAIRS}
    S = {(n, m): inputs[f"s_{n}_{m}"] for n, m in SE_PAIRS}
    cut = {n: inputs[f"cut_{n}"] for n in range(1, top + 1)}
    Np, dN = {}, {}
    for n in range(top, 0, -1):
        cnn = C.get((n, n), 0.0)
        snn = S.get((n, n), 0.0)
        rest = sum(C.get((n, m), 0.0) * (Np[m] + cut[m]) for m in range(n + 1, top + 1))
        Np[n] = (cnn * cut[n] + rest) / (1 - cnn)
        err = snn * (Np[n] + cut[n]) + sum(C.get((n, m), 0.0) * dN[m] + S.get((n, m), 0.0) * (Np[m] + cut[m])
                                           for m in range(n + 1, top + 1))
        dN[n] = err / (1 - cnn)
    k = int(round(inputs["n"]))
    return {"Nx": Np[k], "Ntot": inputs[f"intact_{k}"] + cut[k] + Np[k], "dN": dN[k]}
