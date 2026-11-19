import statistics


def run(inputs, settings):
    # the median, placed at the middle rank of the points so it compares with a line drawn there
    xs = inputs["values"]["x"]
    mid = (min(xs) + max(xs)) / 2.0
    return {"median": {"x": [mid], "y": [float(statistics.median(inputs["values"]["y"]))]}}
