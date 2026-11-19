def run(inputs, settings):
    c = inputs["fold"]
    return {"reduction": {"x": list(c["x"]), "y": [1.0 - y for y in c["y"]]}}
