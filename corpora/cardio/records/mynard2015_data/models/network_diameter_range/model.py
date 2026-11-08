# Adapter (software: true): smallest and largest reference diameter D0 in one or more blocks of the released
# Supplemental File 1 (MOESM1_1D_segments.xlsx, read from $BOXGRAPH_SOURCE). Our own code takes every inlet
# and outlet A0 (columns E and F, cm2) of the segments in the blocks named by settings.blocks (block titles of
# column A, e.g. 'Systemic Arteries') and returns the diameters 2 sqrt(A0/pi) of the smallest and largest.
# A tapered segment's A0 lies between its two ends, so these are the extremes over the network.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mynard2015_data_sheets", os.path.join(_HERE, "..", "network_counts", "_sheets.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def run(inputs, settings):
    segs = [s for s in S.segments() if s["block"] in settings["blocks"]]
    if {s["block"] for s in segs} != set(settings["blocks"]):
        raise ValueError(f"blocks not found: {set(settings['blocks']) - {s['block'] for s in segs}}")
    areas = [s["E"] for s in segs] + [s["F"] for s in segs]
    return {"D_min": S.diameter(min(areas)), "D_max": S.diameter(max(areas))}
