"""One-dimensional model of the 55-segment arterial tree (Eqs. 1-3, 6-9), with the wall law of Eq. 9.

The paper uses the quadratic Eq. 4 with coefficients from Eq. 9 (C0' = K/p0, C1' = -K/(2 p0^2)); its
compliance vanishes at p = 2 p0 = 194 mmHg, which the peripheral systolic pressures exceed, and the
explicit scheme then fails (model arterial_tree_eq4, not runnable). This model uses Eq. 9 itself, which
Eq. 4 approximates:
Continuity (Eq. 1 with Eq. 9):  dQ/dx + A0 (K/p) dp/dt = 0, K = C0' p0, C0' = Cvol/(L A0mean) (p. 3).
Momentum (Eq. 6):    cu dQ/dt + d(Q^2/A0)/dx + (A0/rho) dp/dx + B1 Q = 0, B1 = 8 cv pi mu/(rho A0).
Bifurcations:        pressure continuous, flow conserved.
Terminals (Eq. 7):   R1 in series with (R2 parallel CT), R1 + R2 = RT.
Stenosis (Eq. 8):    dp = 4 Kv mu/(pi D^3) Q + Kt rho/(2 A0^2) (A0/As - 1)^2 Q|Q| + Ku rho Ls/A0 dQ/dt.

Numerics (the paper's thesis scheme is not printed; this is the reader's explicit first-order scheme):
a staggered grid, pressure at cell centres and flow on the faces between cells; faces joining a parent's
last cell to its daughters' first cells form the bifurcations. Flow is advanced first (friction and the
stenosis losses semi-implicitly), then pressure from the new flows (forward-backward Euler). The
convective term is upwinded within each segment and omitted on faces at segment ends.
Everything is in cgs units internally.
"""

import math

import numpy as np

# Topology: daughters of each segment, from Fig. 1 (segments without daughters are the 28 terminals of Table 2)
TREE = {1: (2, 3), 3: (4, 5), 4: (6, 7), 7: (8, 9), 9: (10, 11), 5: (12, 13), 2: (14, 15), 15: (16, 17),
        14: (18, 19), 19: (20, 21), 21: (22, 23), 23: (24, 25), 18: (26, 27), 27: (28, 29), 29: (30, 31),
        30: (32, 33), 28: (34, 35), 35: (36, 37), 37: (38, 39), 39: (40, 41), 41: (42, 43), 43: (44, 45),
        44: (46, 47), 46: (48, 49), 42: (50, 51), 50: (52, 53), 52: (54, 55)}
SEGMENTS = tuple(range(1, 56))
TERMINALS = tuple(s for s in SEGMENTS if s not in TREE)
MMHG = 1333.22368  # dyn/cm^2


def _downstream_terminals(s):
    if s not in TREE:
        return [s]
    out = []
    for d in TREE[s]:
        out += _downstream_terminals(d)
    return out


def _build(inp, settings):
    dx_target = settings["dx"]
    rho, mu, cu, cv = inp["rho"], inp["mu"], inp["cu"], inp["cv"]
    p0 = inp["p0"]
    cells = {}  # segment -> slice of cell indices
    A0c, Cc, dxc, segc = [], [], [], []
    for s in SEGMENTS:
        L, rp, rd, Cvol = inp[f"L_{s}"], inp[f"rp_{s}"], inp[f"rd_{s}"], inp[f"Cv_{s}"]
        n = max(2, int(math.ceil(L / dx_target - 1e-9)))
        dx = L / n
        Ap, Ad = math.pi * rp ** 2, math.pi * rd ** 2
        Amean = 0.5 * (Ap + Ad)
        C0p = Cvol / (L * Amean)  # C0' (p. 3)
        start = len(A0c)
        for i in range(n):
            xi = (i + 0.5) / n
            A = Ap + (Ad - Ap) * xi  # area varies linearly along the segment
            A0c.append(A)
            Cc.append(C0p * A * dx)  # C0' A0 dx; the pressure factor p0/p is applied each step
            dxc.append(dx)
            segc.append(s)
        cells[s] = (start, start + n)
    A0c, Cc, dxc = np.array(A0c), np.array(Cc), np.array(dxc)
    # faces: (upstream cell, downstream cell, inertance, resistance, area, prev face, next face)
    up, dn, ine, res, area, prv, nxt, fseg = [], [], [], [], [], [], [], []
    seg_faces = {}
    for s in SEGMENTS:
        a, b = cells[s]
        first = len(up)
        for i in range(a, b - 1):
            A = 0.5 * (A0c[i] + A0c[i + 1])
            le = 0.5 * (dxc[i] + dxc[i + 1])
            up.append(i)
            dn.append(i + 1)
            ine.append(cu * rho * le / A)
            res.append(8 * cv * math.pi * mu * le / A ** 2)
            area.append(A)
            fseg.append(s)
        seg_faces[s] = (first, len(up))
    for f in range(len(up)):
        s = fseg[f]
        a, b = seg_faces[s]
        prv.append(f - 1 if f - 1 >= a else -1)
        nxt.append(f + 1 if f + 1 < b else -1)
    for s, (d1, d2) in sorted(TREE.items()):
        last = cells[s][1] - 1
        for d in (d1, d2):
            firstd = cells[d][0]
            le_p, le_d = 0.5 * dxc[last], 0.5 * dxc[firstd]
            up.append(last)
            dn.append(firstd)
            ine.append(cu * rho * (le_p / A0c[last] + le_d / A0c[firstd]))
            res.append(8 * cv * math.pi * mu * (le_p / A0c[last] ** 2 + le_d / A0c[firstd] ** 2))
            area.append(A0c[firstd])
            prv.append(-1)
            nxt.append(-1)
            fseg.append(d)
    net = {
        "cells": cells, "A0c": A0c, "Cc": Cc, "dxc": dxc, "segc": np.array(segc),
        "up": np.array(up), "dn": np.array(dn), "ine": np.array(ine), "res": np.array(res),
        "area": np.array(area), "prv": np.array(prv), "nxt": np.array(nxt), "fseg": np.array(fseg),
        "seg_faces": seg_faces, "p0": p0, "rho": rho, "mu": mu,
    }
    # wave speed at p0 for the stability check, c = sqrt(A0/(rho dA/dp)), dA/dp = C0' A0 at p0
    net["c_max"] = float(np.max(np.sqrt(A0c * dxc / (rho * Cc))))
    net["dt_cfl"] = float(np.min(dxc / np.sqrt(A0c * dxc / (rho * Cc))))
    return net


def _simulate(inp, settings, stenosis_pct, rt_scale_distal, distal):
    """One run of n_cycles heart cycles; returns per-cell and per-face records over the last cycle."""
    net = _build(inp, settings)
    dt = settings["dt"]
    if dt > net["dt_cfl"]:
        raise ValueError(f"dt = {dt} s exceeds the stability limit dx/c = {net['dt_cfl']:.2e} s")
    T, Ts, Qmax = inp["T"], inp["Ts"], inp["Qmax"]
    pv = inp["pv"]
    p0 = net["p0"]
    up, dn, ine, res = net["up"], net["dn"], net["ine"].copy(), net["res"].copy()
    prv, nxt, area = net["prv"], net["nxt"], net["area"]
    Cc = net["Cc"]
    ncell = len(Cc)
    nface = len(up)
    # stenosis on the face nearest the middle of the stenosed segment
    sten_face = -1
    knl = 0.0
    if stenosis_pct > 0:
        s = int(settings["stenosis_segment"])
        a, b = net["seg_faces"][s]
        sten_face = (a + b - 1) // 2
        A0 = area[sten_face]
        D0 = math.sqrt(4 * A0 / math.pi)
        As = A0 * (1 - stenosis_pct / 100.0)
        Ds = math.sqrt(4 * As / math.pi)
        Ls = inp["Ls"]
        Kv = 32.0 * (inp["kv_a"] * Ls + inp["kv_b"] * Ds) / D0 * (A0 / As) ** 2
        res[sten_face] += 4 * Kv * net["mu"] / (math.pi * D0 ** 3)
        knl = inp["Kt"] * net["rho"] / (2 * A0 ** 2) * (A0 / As - 1) ** 2
        ine[sten_face] += inp["Ku"] * net["rho"] * Ls / A0
    # terminals
    tcell = np.array([net["cells"][s][1] - 1 for s in TERMINALS])
    RT = np.array([inp[f"RT_{s}"] for s in TERMINALS])
    CT = np.array([inp[f"CT_{s}"] for s in TERMINALS])
    scale = np.array([rt_scale_distal if s in distal else 1.0 for s in TERMINALS])
    RT = RT * scale
    R1 = inp["R1_ratio"] * RT
    R2 = RT - R1
    inlet = net["cells"][1][0]
    # initial state: the mean pressure the mean inflow would give through the terminal resistances
    Qmean_in = Qmax * 2 * Ts / (math.pi * T)
    p_init = pv + Qmean_in / np.sum(1.0 / RT)
    p = np.full(ncell, p_init)
    pwk = pv + (p_init - pv) * R2 / RT
    Q = np.zeros(nface)
    nsteps = int(round(T / dt))
    ncyc = int(settings["n_cycles"])
    rec_every = int(settings.get("record_every", 1))
    P_rec = np.zeros((nsteps // rec_every + 1, ncell))
    Q_rec = np.zeros((nsteps // rec_every + 1, nface))
    Qin_rec = np.zeros(nsteps // rec_every + 1)
    Qt_rec = np.zeros((nsteps // rec_every + 1, len(TERMINALS)))
    has_prev, has_next = prv >= 0, nxt >= 0
    prv_i, nxt_i = np.where(has_prev, prv, 0), np.where(has_next, nxt, 0)
    for k in range(ncyc):
        last = k == ncyc - 1
        for n in range(nsteps):
            t = (n + 1) * dt
            tc = t % T
            qin = Qmax * math.sin(math.pi * tc / Ts) if tc < Ts else 0.0
            # momentum: convective term d(Q^2/A0)/dx upwinded within segments
            F = Q * Q / area
            conv = np.where(Q >= 0, np.where(has_prev, F - F[prv_i], 0.0), np.where(has_next, F[nxt_i] - F, 0.0))
            le_conv = net["rho"] / area  # (rho/A0) * d(Q^2/A0) integrated over one face spacing
            drive = p[up] - p[dn] - le_conv * conv
            rtot = res.copy()
            if sten_face >= 0:
                rtot[sten_face] += knl * abs(Q[sten_face])
            Q = (Q + dt / ine * drive) / (1 + dt * rtot / ine)
            # terminal outflow through R1 into the windkessel node
            qt = (p[tcell] - pwk) / R1
            # continuity
            dV = np.zeros(ncell)
            np.add.at(dV, dn, Q)
            np.add.at(dV, up, -Q)
            dV[inlet] += qin
            dV[tcell] -= qt
            comp = Cc * (p0 / p)  # dA/dp = A0 K / p from Eq. 9, K = C0' p0
            p = p + dt * dV / comp
            pwk = pwk + dt * (qt - (pwk - pv) / R2) / CT
            if last and n % rec_every == 0:
                j = n // rec_every
                P_rec[j] = p
                Q_rec[j] = Q
                Qin_rec[j] = qin
                Qt_rec[j] = qt
        if not np.all(np.isfinite(p)):
            raise FloatingPointError("the simulation diverged")
    m = nsteps // rec_every
    return net, P_rec[:m], Q_rec[:m], Qin_rec[:m], Qt_rec[:m], sten_face


def _cell_at(net, seg, where):
    a, b = net["cells"][seg]
    if where == "proximal":
        return a
    if where == "distal":
        return b - 1
    return (a + b - 1) // 2


def _face_in_seg(net, seg, where):
    a, b = net["seg_faces"][seg]
    if where == "proximal":
        return a
    if where == "distal":
        return b - 1
    return (a + b - 1) // 2


def _summary(inp, settings, pct, rt_scale):
    seg = int(settings["stenosis_segment"])
    distal = set(_downstream_terminals(seg))
    net, P, Qf, Qin, Qt, sf = _simulate(inp, settings, pct, rt_scale, distal)
    a, b = net["seg_faces"][seg]
    q_seg = Qf[:, (a + b - 1) // 2]
    brach = P[:, _cell_at(net, int(settings["brachial_segment"]), "middle")].max()
    thigh = P[:, _cell_at(net, 46, "proximal")].max()
    knee = P[:, _cell_at(net, 46, "distal")].max()
    ankle = P[:, _cell_at(net, 48, "distal")].max()
    # flow just distal to the stenosis (next face in the segment) and at the distal end of the L. posterior tibial
    q_dist = Qf[:, (a + b - 1) // 2 + 1]
    q_ankle = Qf[:, _face_in_seg(net, 48, "distal")]

    def pi(q):
        return (q.max() - q.min()) / q.mean()

    asc = P[:, _cell_at(net, 1, "proximal")]
    return {
        "q_seg": float(q_seg.mean()),
        "sys_thigh": thigh / brach, "sys_knee": knee / brach, "sys_ankle": ankle / brach,
        "pi_dist": pi(q_dist), "pi_ankle": pi(q_ankle),
        "p_asc_sys": float(asc.max()), "p_asc_dia": float(asc.min()), "p_asc_mean": float(asc.mean()),
        "q_in_mean": float(Qin.mean()),
    }


def run(inputs, settings):
    pct = inputs["stenosis"]
    base = _summary(inputs, settings, 0.0, 1.0)
    out = {}
    if settings.get("autoregulate"):
        # distal vasodilation: scale the distal terminal resistances so the mean flow through the
        # stenosed segment returns to its normal (0% stenosis) value; secant iteration on the scale
        target = base["q_seg"]
        f0, f1 = 1.0, 0.8
        s0 = _summary(inputs, settings, pct, f0)
        g0 = s0["q_seg"] - target
        s1 = _summary(inputs, settings, pct, f1)
        g1 = s1["q_seg"] - target
        for _ in range(int(settings["max_iter"])):
            if abs(g1) <= settings["flow_tol"] * target:
                break
            f2 = f1 - g1 * (f1 - f0) / (g1 - g0)
            f2 = min(max(f2, 0.01), 1.0)
            f0, g0 = f1, g1
            f1 = f2
            s1 = _summary(inputs, settings, pct, f1)
            g1 = s1["q_seg"] - target
        sten = s1
        out["rt_reduction"] = 100.0 * (1.0 - f1)
    else:
        sten = _summary(inputs, settings, pct, 1.0) if pct > 0 else base
        out["rt_reduction"] = 0.0
    out.update({
        "dt_max": _build(inputs, settings)["dt_cfl"],
        "Q_ratio": sten["q_seg"] / base["q_seg"],
        "sys_ratio_thigh": sten["sys_thigh"], "sys_ratio_knee": sten["sys_knee"], "sys_ratio_ankle": sten["sys_ankle"],
        "PI_ratio_distal": sten["pi_dist"] / base["pi_dist"], "PI_ratio_ankle": sten["pi_ankle"] / base["pi_ankle"],
        "p_asc_sys": sten["p_asc_sys"] / MMHG, "p_asc_dia": sten["p_asc_dia"] / MMHG,
        "p_asc_mean": sten["p_asc_mean"] / MMHG,
    })
    return out
