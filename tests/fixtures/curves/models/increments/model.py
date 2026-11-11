def run(inputs, settings):
    x, y = inputs["U"]["x"], inputs["U"]["y"]
    return {"dU": {"x": x, "y": [0.0] + [y[i] - y[i - 1] for i in range(1, len(y))]}}
