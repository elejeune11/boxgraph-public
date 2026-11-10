# Pixels per cell (p. 35): the mean stained-cell area divided by the area of one pixel, the square of the
# image resolution. Area in um^2, resolution in um per pixel.
def run(inputs, settings):
    return {"n_px": inputs["area"] / inputs["res"] ** 2}


def symbolic():
    import sympy as sp

    area, res = sp.symbols("area res", positive=True)
    return {"n_px": area / res ** 2}
