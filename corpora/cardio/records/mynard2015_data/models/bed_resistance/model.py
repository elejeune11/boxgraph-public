# Adapter (software: true): the released bed resistances (MOESM2_vascular_beds.xlsx, column D, mmHg s/mL; read
# from $BOXGRAPH_SOURCE) combined into one systemic and one pulmonary resistance, and the arterial time constant
# R x Cart of the systemic beds. Our own code:
#   pulmonary: the beds of the block 'Pulmonary Vascular Beds' in parallel;
#   systemic: the beds of 'Systemic Vascular Beds' in parallel, except that the beds of settings.splanchnic (the
#   hepatic arterial compartment and the beds draining into the portal veins) are first combined in parallel and
#   then put in series with the liver lobules (Fig. 2b); with settings.include_coronary, the nine coronary
#   layers of 'Coronary Vascular Beds' (which drain to the right atrium through the coronary sinus) are added in
#   parallel. 1D segment resistances are not included.
#   tau: R x Arterial Compliance (column E) of each systemic bed other than the liver rows: the brain's (row
#   'Brain'), and the smallest and largest of the others.
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mynard2015_data_sheets", os.path.join(_HERE, "..", "network_counts", "_sheets.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def run(inputs, settings):
    beds = S.beds()
    sysb = [b for b in beds if b["block"] == "Systemic Vascular Beds"]
    cor = [b for b in beds if b["block"] == "Coronary Vascular Beds"]
    pul = [b for b in beds if b["block"].startswith("Pulmonary Vascular Beds")]
    lobules = [b for b in sysb if b["B"] == "Liver (lobules)"]
    splanch = [b for b in sysb if b["B"] in settings["splanchnic"]]
    if len(lobules) != 1 or len(splanch) != len(settings["splanchnic"]):
        raise ValueError("liver rows not found")
    others = [b for b in sysb if b not in lobules and b not in splanch]
    g = sum(1.0 / b["D"] for b in others)
    g += 1.0 / (1.0 / sum(1.0 / b["D"] for b in splanch) + lobules[0]["D"])
    if settings["include_coronary"]:
        g += sum(1.0 / b["D"] for b in cor)
    generic = [b for b in sysb if not b["B"].startswith("Liver")]
    brain = [b for b in generic if b["B"] == "Brain"]
    rest = [b["D"] * b["E"] for b in generic if b["B"] != "Brain"]
    return {"R_sys": 1.0 / g, "R_pulm": 1.0 / sum(1.0 / b["D"] for b in pul),
            "tau_brain": brain[0]["D"] * brain[0]["E"], "tau_min_other": min(rest), "tau_max_other": max(rest)}
