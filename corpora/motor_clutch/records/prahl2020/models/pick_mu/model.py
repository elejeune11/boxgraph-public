# The value of a read curve at one of its x positions (setting `at`): picks one condition out of a
# figure reading so that it can be set beside a value printed in the text.


def run(inputs, settings):
    c = inputs["c"]
    i = min(range(len(c["x"])), key=lambda k: abs(c["x"][k] - settings["at"]))
    if abs(c["x"][i] - settings["at"]) > 1e-6 * max(1.0, abs(settings["at"])):
        raise ValueError(f"no point at x = {settings['at']}")
    return {"y": c["y"][i]}
