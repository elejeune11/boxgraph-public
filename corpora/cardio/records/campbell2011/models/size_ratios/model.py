# Plain ratios. Applied to group medians they give a ratio of medians, which the paper's
# median of per-patient ratios need not equal (question q_ratio_of_medians).
def run(inputs, settings):
    R, w, B, M = inputs["R"], inputs["w"], inputs["B"], inputs["M"]
    return {"RB": R / B, "RM": R / M, "Rw": R / w, "wB": w / B, "wM": w / M}


def symbolic():
    import sympy as sp
    R, w, B, M = sp.symbols("R w B M", positive=True)
    return {"RB": R / B, "RM": R / M, "Rw": R / w, "wB": w / B, "wM": w / M}
