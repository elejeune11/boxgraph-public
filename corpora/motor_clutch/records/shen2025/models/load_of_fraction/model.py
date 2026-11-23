# External load as a fraction of the steady motor force (Fig. 12 caption, Fig. 13 caption):
# F~ = load * nm0 f~s, with nm0 = w~ Nm / (w~ + exp(f~s/f~d)) (Eq. 10).
import math


def run(inputs, settings):
    nm0 = inputs["w"] * inputs["Nm"] / (inputs["w"] + math.exp(inputs["fs"] / inputs["fd"]))
    return {"F": inputs["load"] * nm0 * inputs["fs"]}


def symbolic():
    import sympy as sp
    w, Nm, fs, fd, load = sp.symbols("w Nm fs fd load", positive=True)
    return {"F": load * w * Nm / (w + sp.exp(fs / fd)) * fs}
