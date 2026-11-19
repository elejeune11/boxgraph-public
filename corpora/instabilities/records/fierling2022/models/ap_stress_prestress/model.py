# The paper (p. 6): "The AP stress sigma_AP is found approximately equal to the pre-stress sigma_a
# initially imposed on the ventral region", i.e. AP strain ~ 0 so the AP stress is the pre-stress.


def run(inputs, settings):
    c = inputs["sigma_a"]
    return {"sigma_AP": {"x": list(c["x"]), "y": list(c["y"])}}
