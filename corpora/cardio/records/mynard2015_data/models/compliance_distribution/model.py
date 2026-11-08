# Adapter (software: true): the distribution of vascular compliance (the paper's Table 3) as the released
# networks and beds give it, read from $BOXGRAPH_SOURCE. Our own code:
#   0D (MOESM2_vascular_beds.xlsx): block 'Systemic Vascular Beds': Arterial Compliance (column E) of every bed
#   but the liver lobules -> systemic arteries; Venous Compliance (column F) of every bed -> systemic veins;
#   the liver lobules' column E (the lobular compliance Cp/a of Fig. 2b) -> systemic veins. Liver: columns E
#   and F of the row 'Liver (lobules)'. Block 'Pulmonary Vascular Beds': E -> pulmonary arteries, F ->
#   pulmonary veins. Block 'Coronary Vascular Beds' (intramyocardial C1, C2): left out, or with
#   settings.include_coronary_beds E -> systemic arteries and F -> systemic veins.
#   1D (MOESM1_1D_segments.xlsx): compliance of a segment = integral of A0 / (rho c0^2) over its length (the
#   area compliance dA/dp at the reference state of a tube whose wave speed is c0), with c0 from the paper's
#   Eq. 3 using the coefficients of the block's network (settings.coefficients), the radius linear between
#   inlet and outlet (midpoint rule, settings.n_taper points), times N for a '[xN]' segment; cgs units, then
#   1 mmHg = 1333.22387415 dyn/cm2. Blocks are summed by settings.regions.
#   C_total: the four regions summed (the liver is inside systemic veins).
import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mynard2015_data_sheets", os.path.join(_HERE, "..", "network_counts", "_sheets.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

MMHG = 1333.22387415  # dyn/cm2


def _segment_compliance(s, rho, k, n):
    k1, k2, k3 = k
    r1, r2 = math.sqrt(s["E"] / math.pi), math.sqrt(s["F"] / math.pi)
    total = 0.0
    for i in range(n):
        r = r1 + (r2 - r1) * (i + 0.5) / n
        c2 = 2.0 / (3.0 * rho) * (k1 * math.exp(k2 * r) + k3)
        total += math.pi * r * r / (rho * c2) * s["D"] / n
    return total * S.multiplicity(s) * MMHG


def run(inputs, settings):
    rho = inputs["rho"]
    k = {net: (inputs[f"k1_{net}"], inputs[f"k2_{net}"], inputs[f"k3_{net}"])
         for net in ("sa", "sv", "pa", "pv", "ca", "cv")}
    by_block = {}
    for s in S.segments():
        net = settings["coefficients"][s["block"]]
        by_block[s["block"]] = by_block.get(s["block"], 0.0) + _segment_compliance(s, rho, k[net], settings["n_taper"])
    c1d = {reg: sum(by_block[b] for b in blocks) for reg, blocks in settings["regions"].items()}
    if set().union(*settings["regions"].values()) != set(by_block):
        raise ValueError("every block must be in exactly one region")
    c0d = {"sys_art": 0.0, "sys_vein": 0.0, "pulm_art": 0.0, "pulm_vein": 0.0}
    liver = None
    for b in S.beds():
        ca, cv = b["E"] or 0.0, b["F"] or 0.0
        if b["block"] == "Systemic Vascular Beds":
            if b["B"] == "Liver (lobules)":
                c0d["sys_vein"] += ca + cv
                liver = ca + cv
            else:
                c0d["sys_art"] += ca
                c0d["sys_vein"] += cv
        elif b["block"].startswith("Pulmonary Vascular Beds"):
            c0d["pulm_art"] += ca
            c0d["pulm_vein"] += cv
        elif b["block"] == "Coronary Vascular Beds":
            if settings["include_coronary_beds"]:
                c0d["sys_art"] += ca
                c0d["sys_vein"] += cv
        else:
            raise ValueError(f"unknown bed block {b['block']!r}")
    out = {f"C_{r}": c1d[r] + c0d[r] for r in c0d}
    out.update({f"C1d_{r}": c1d[r] for r in c0d})
    out.update({f"C0d_{r}": c0d[r] for r in c0d})
    out["C_liver"] = liver
    out["C_total"] = sum(out[f"C_{r}"] for r in c0d)
    return out
