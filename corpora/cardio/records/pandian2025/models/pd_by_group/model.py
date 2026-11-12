# The value printed for the group whose bar is at x (1 control, 2 IL-1beta). Units m/s in and out.
def run(inputs, settings):
    g = int(round(inputs["group"]))
    return {"Pd": inputs["Pd_ctl"] if g == 1 else inputs["Pd_il1b"]}
