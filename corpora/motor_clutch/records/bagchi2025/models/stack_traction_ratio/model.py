def run(inputs, settings):
    pts = dict(zip(inputs["T"]["x"], inputs["T"]["y"]))
    red = [y for x, y in pts.items() if round(x) == 1][0]
    blue = [y for x, y in pts.items() if round(x) == 2][0]
    return {"ratio_stacked": (blue - red) / red, "ratio_overlaid": blue / red}
