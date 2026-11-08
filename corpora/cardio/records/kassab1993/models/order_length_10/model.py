def run(inputs, settings):
    n = int(round(inputs["n"]))
    if not 1 <= n <= 10:
        raise ValueError(f"order {n} outside 1-10")
    return {"y": inputs[f"v{n}"]}
