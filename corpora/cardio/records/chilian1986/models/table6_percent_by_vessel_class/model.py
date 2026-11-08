# The printed Table 6 Mean% of the chosen vessel class, so that Table 6 can be set beside the points
# of Fig. 7 (1 large arterioles, 2 medium arterioles, 3 small venules, 4 medium venules).
# Units: percent in and out.


def run(inputs, settings):
    k = int(round(inputs["cls"]))
    if k not in (1, 2, 3, 4):
        raise ValueError(f"vessel class must be 1-4, got {inputs['cls']}")
    return {"pct": inputs[f"pct_{k}"]}
