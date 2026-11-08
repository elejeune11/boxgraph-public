# Adapter (software: true): the coronary venous diameters by the paper's rule (p. 6), applied to the released
# coronary arteries, and the released coronary sinus diameter (Supplemental File 1, MOESM1_1D_segments.xlsx,
# blocks 'Coronary Arteries' and 'Coronary Veins', read from $BOXGRAPH_SOURCE). Our own code:
#   terminal veins: the veins whose inlet (column G) is a bed 'VB:<name>'; their artery is the coronary artery
#   whose outlet (column H) is the same bed. D_vein = ratio * D_artery, from the outlet A0 of the artery
#   (column F) ('a vein-to-artery diameter ratio of 1.4 was used for the terminal veins');
#   non-terminal veins: D^xi = sum of D^xi of the veins draining into them (column G), applied repeatedly
#   toward the coronary sinus ('repeated application of Eq. (2a)', generalised to three inflows where the
#   coronary sinus receives three veins);
#   ratio_min, ratio_max: the released D_vein / D_artery of the terminal pairs (inlet A0 of the vein, outlet A0
#   of the artery);
#   D_cs_released: the released diameter of settings.sinus, from its inlet A0 (column E).
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mynard2015_data_sheets", os.path.join(_HERE, "..", "network_counts", "_sheets.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def run(inputs, settings):
    ratio, xi = inputs["ratio"], inputs["xi"]
    segs = S.segments()
    arteries = [s for s in segs if s["block"] == "Coronary Arteries"]
    veins = {s["C"]: s for s in segs if s["block"] == "Coronary Veins"}
    art_of_bed = {}
    for a in arteries:
        for t in S.names(a["H"]):
            if t.startswith("VB:"):
                art_of_bed[t] = a
    memo, released = {}, []

    def D(name):
        if name in memo:
            return memo[name]
        v = veins[name]
        inflow = S.names(v["G"])
        beds = [t for t in inflow if t.startswith("VB:")]
        if beds:
            if len(inflow) != 1:
                raise ValueError(f"{name}: mixed inflow {inflow}")
            a = art_of_bed[beds[0]]
            d = ratio * S.diameter(a["F"])
            released.append(S.diameter(v["E"]) / S.diameter(a["F"]))
        else:
            d = sum(D(n) ** xi for n in inflow) ** (1.0 / xi)
        memo[name] = d
        return d

    d_cs = D(settings["sinus"])
    return {"D_cs_rule": d_cs, "D_cs_released": S.diameter(veins[settings["sinus"]]["E"]),
            "ratio_min": min(released), "ratio_max": max(released)}
