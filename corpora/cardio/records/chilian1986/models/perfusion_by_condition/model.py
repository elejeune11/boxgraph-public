# The group-mean perfusion of the chosen condition, so that Table 3 can be set beside the bars of
# Fig. 4 (1 control, 2 papaverine). Units: ml/min/hg in and out.


def run(inputs, settings):
    c = int(round(inputs["condition"]))
    if c == 1:
        return {"Q": inputs["Q_ctl"]}
    if c == 2:
        return {"Q": inputs["Q_pap"]}
    raise ValueError(f"condition must be 1 (control) or 2 (papaverine), got {inputs['condition']}")
