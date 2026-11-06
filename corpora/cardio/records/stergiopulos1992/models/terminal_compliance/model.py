"""Terminal compliances, C_Ti = C_vol,res Q_i/Q_total = C_vol,res R_total/R_Ti (p. 3).

R_total is taken as the parallel combination of the 28 terminal resistances of Table 2, so that the
C_Ti add up to C_vol,res (the residual compliance "distributed among the terminal branches").
"""

TERMINALS = (6, 8, 10, 11, 12, 13, 16, 17, 20, 22, 24, 25, 26, 31, 32, 33, 34, 36, 38, 40, 45, 47, 48, 49,
             51, 53, 54, 55)
MMHG_PA = 133.322368  # Pa per mmHg


def run(inputs, settings):
    # ports: Cres in mL/mmHg, RT in N*s/m^5; outputs in m^5/N
    cres = inputs["Cres"] * 1e-6 / MMHG_PA  # m^3/Pa = m^5/N
    rtot = 1.0 / sum(1.0 / inputs[f"RT_{s}"] for s in TERMINALS)
    return {f"CT_{s}": cres * rtot / inputs[f"RT_{s}"] for s in TERMINALS}
