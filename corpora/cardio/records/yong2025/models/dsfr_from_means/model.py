# Ratio of a mean diastolic to a mean systolic flow: how Table 1's mDSFR relates to its own
# mean-flow rows. Port units: ml/s in, dimensionless out.


def run(inputs, settings):
    return {"ratio": inputs["Qd_mean"] / inputs["Qs_mean"]}
