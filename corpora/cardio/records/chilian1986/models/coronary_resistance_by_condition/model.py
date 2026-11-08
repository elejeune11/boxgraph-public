# The coronary_resistance rule (R = P / Q, Methods p. 4) applied to the group of the chosen
# condition, so that it can be run over the bars of Fig. 4 (1 control, 2 papaverine).
# Units: mmHg and ml/min/hg in, mmHg*min*hg/ml out.


def run(inputs, settings):
    c = int(round(inputs["condition"]))
    if c == 1:
        return {"R": inputs["P_ctl"] / inputs["Q_ctl"]}
    if c == 2:
        return {"R": inputs["P_pap"] / inputs["Q_pap"]}
    raise ValueError(f"condition must be 1 (control) or 2 (papaverine), got {inputs['condition']}")
