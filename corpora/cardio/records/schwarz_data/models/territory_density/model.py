# Our own reading of the perfusion definition (explanation_of_data.txt lines 163 and 216): each
# territory weighs heart weight * VVoronoi / sum(all Voronoi volumes), so the left coronary tree's
# territories together weigh weighttot * Vtree_of_Vtot. Over the tree's perfused volume that is the
# tissue density the perfusion values imply. Ports: W in kg, V in cm^3; W_tree in g, rho in g/cm^3.
def run(inputs, settings):
    w_tree = inputs["W"] * 1000.0 * inputs["f"]
    return {"W_tree": w_tree, "rho": w_tree / inputs["V"]}


def symbolic():
    import sympy as sp
    W, f, V = sp.symbols("W f V", positive=True)
    return {"W_tree": 1000 * W * f, "rho": 1000 * W * f / V}
