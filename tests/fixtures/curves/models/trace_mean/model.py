def run(inputs, settings):
    x, y = inputs["U"]["x"], inputs["U"]["y"]
    area = sum((x[i + 1] - x[i]) * (y[i + 1] + y[i]) / 2 for i in range(len(x) - 1))
    return {"U_mean": area / (x[-1] - x[0])}
