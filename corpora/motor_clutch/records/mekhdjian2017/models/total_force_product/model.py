# Total traction force as average traction stress times cell spread area (Fig. 5 legend (e)), point by point
# over two curves indexed by gel modulus. Pa * um^2 = 1e-12 N = 1e-3 nN.


def run(inputs, settings):
    T, A = inputs["T"], inputs["A"]
    a = dict(zip(A["x"], A["y"]))
    xs = [x for x in T["x"] if x in a]
    t = dict(zip(T["x"], T["y"]))
    return {"F": {"x": xs, "y": [t[x] * a[x] * 1e-3 for x in xs]}}
