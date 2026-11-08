def run(inputs, settings):
    n = int(round(inputs["n"]))
    if not 1 <= n <= 11:
        raise ValueError(f"order {n} outside 1-11")
    return {"y": inputs[f"v{n}"]}
