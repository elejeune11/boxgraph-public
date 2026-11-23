# The substrate modulus at which a traction-stress curve is largest: the "optimum stiffness" the text
# reads off Fig. 5c. Takes the curve's own points (no interpolation between them).


def run(inputs, settings):
    c = inputs["T"]
    pts = [(x, y) for x, y in zip(c["x"], c["y"]) if y is not None]
    x, _ = max(pts, key=lambda p: p[1])
    return {"E_opt": x}
