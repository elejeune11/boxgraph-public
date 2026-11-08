# The pressure_percent_of_aortic rule (mean%, Methods p. 5) applied to the group means of the chosen
# vessel class, so that it can be run over the points of Fig. 7 (1 large arterioles, 2 medium
# arterioles, 3 small venules, 4 medium venules). Units: mmHg in, percent out.


def run(inputs, settings):
    k = int(round(inputs["cls"]))
    if k not in (1, 2, 3, 4):
        raise ValueError(f"vessel class must be 1-4, got {inputs['cls']}")
    return {"pct": 100.0 * inputs[f"Pm_{k}"] / inputs[f"Pa_{k}"]}
