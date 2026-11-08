def run(inputs, settings):
    return {"total": sum(inputs[f"N{n}"] for n in range(1, 12))}
