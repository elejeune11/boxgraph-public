# Arranges the rebuild's results for the four configurations of Fig. 7C-D (1 Norm VR+IMP,
# 2 PH VR+IMP, 3 Norm Rbar+IMP, 4 PH Rbar+IMP) by bar position, so they can be compared with
# the bars read from the figure. Lower segment: the systolic part of the cycle mean, mean systolic flow times the systolic share of the cycle (Qs_mean x sys_frac / 100).


def run(inputs, settings):
    k = int(round(inputs["bar"]))
    if k not in (1, 2, 3, 4):
        return {"Q_sys": float("nan")}
    return {"Q_sys": inputs[f"qs{k}"] * inputs[f"f{k}"] / 100.0}
