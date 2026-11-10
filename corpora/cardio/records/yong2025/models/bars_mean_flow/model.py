# Arranges the rebuild's results for the four configurations of Fig. 7C-D (1 Norm VR+IMP,
# 2 PH VR+IMP, 3 Norm Rbar+IMP, 4 PH Rbar+IMP) by bar position, so they can be compared with
# the bars read from the figure. Bar height: the cycle-mean flow of that configuration.


def run(inputs, settings):
    k = int(round(inputs["bar"]))
    if k not in (1, 2, 3, 4):
        return {"Q": float("nan")}
    return {"Q": inputs[f"v{k}"]}
