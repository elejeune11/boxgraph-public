"""Volume compliance of the arterial segments of the model: the sum of the 55 Table 1 values (p. 3)."""

MMHG_DYN_CM2 = 1333.22368  # dyn/cm^2 per mmHg


def run(inputs, settings):
    # ports are cm^5/Mdyn (1e-6 cm^5/dyn, the Table 1 unit); the output is mL/mmHg
    total = sum(inputs[f"Cv_{s}"] for s in range(1, 56)) * 1e-6  # cm^5/dyn = mL per dyn/cm^2
    return {"Csum": total * MMHG_DYN_CM2}
