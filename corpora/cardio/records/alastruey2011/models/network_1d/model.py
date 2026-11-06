"""Nonlinear 1-D model of the 37-artery silicone network (Eqs. 1 and 5), purely elastic or Voigt visco-elastic.

As printed (pp. 2-3), in the conservative form of p. 3:
  dA/dt + d(AU)/dx = 0
  dU/dt + d/dx[U^2/2 + (Pext + Pe)/rho - Gamma/(rho A0 sqrt(A)) d(AU)/dx] = f/(rho A),  f = -22 mu pi U
  Pe = (beta/A0)(sqrt(A) - sqrt(A0))   (elastic part of Eq. 5)
The purely elastic formulation has Gamma = 0. beta is taken from the initial wave speed of Table 2,
c0^2 = beta/(2 rho sqrt(A0)), which is what Eq. 5 gives for c^2 = (A/rho) dP/dA at A = A0; r0 and c0 vary
linearly from inlet to outlet of each segment; Gamma is the value of Table 2.

Numerics. The paper's spectral/hp discontinuous Galerkin scheme with Adams-Bashforth time stepping is not
reproduced; this is the reader's scheme, recorded as a choice. Each segment is divided into cells (a
discontinuous Galerkin scheme of order zero, made second order by MUSCL-Hancock reconstruction of P and U).
Interface fluxes are upwinded through the Riemann invariants W = U +- 4(c - c0), c = sqrt(beta/(2 rho A0)) A^(1/4),
as in Sherwin et al. (2003) for the elastic flux. Segment ends (p. 4; Matthys et al. 2007, as the reader
understands it) take their state from the outgoing invariant and
  inlet:      A U = Qin(t)
  junctions:  mass conserved, total pressure P + rho U^2/2 continuous
  terminals:  A U = (P - Pout)/Rp
The visco-elastic flux is applied after each elastic step by an implicit (backward Euler) step for U with A
frozen, and, as in the paper, is neglected at the boundary conditions and junctions (zero there).
Initial conditions: zero pressure (A = A0) and zero velocity (p. 4). The last of n_cycles cycles is sampled
every sample_dt; P (Pa) and Q (m^3/s) are reported at the midpoint of a segment at time t_cycle into that cycle.

A sweep over t_cycle calls run() once per time point with identical other inputs; the simulation for those
inputs is kept in _MEMO so it is not repeated within one process. It never changes a result.
"""

import math

import numpy as np
from scipy.linalg import solve_banded

N_SEG = 37
# parent -> daughters (Fig. 1, right, and the anatomy of Table 2's names)
TREE = {1: (2, 8), 2: (3, 4), 4: (5,), 5: (6, 7), 8: (9, 10), 10: (11, 15), 11: (12,), 12: (13, 14),
        15: (16, 17), 17: (18, 23), 18: (19, 22), 19: (20, 21), 23: (24, 25), 25: (26, 27), 27: (28, 31),
        28: (29,), 29: (30,), 30: (34, 35), 31: (32,), 32: (33,), 33: (36, 37)}
TERMINALS = (3, 6, 7, 9, 13, 14, 16, 20, 21, 22, 24, 26, 34, 35, 36, 37)
SITES = (3, 7, 10, 11, 14, 15, 17, 20, 24, 29, 30, 34)  # segment midpoints reported

_MEMO = {}


def _inflow(inp, t):
    T = inp["T"]
    s = inp["Qa0"]
    for k in range(1, 21):
        s = s + inp[f"Qa{k}"] * math.sin(2 * math.pi * k * t / T + inp[f"Qph{k}"])
    return s * 1e-3 / 60.0  # L/min -> m^3/s


def _minmod(a, b):
    return np.where(a * b > 0, np.sign(a) * np.minimum(np.abs(a), np.abs(b)), 0.0)


class Net:
    pass


def _build(inp, st):
    rho = inp["rho"]
    dx_t = st["dx"]
    net = Net()
    off, n_of, dx_of = {}, {}, {}
    cA0, cb, cG, cdx = [], [], [], []  # cells
    fA0, fb = [], []  # faces, n + 1 per segment
    for s in range(1, N_SEG + 1):
        L = inp[f"L_{s}"]
        n = int(math.ceil(L / dx_t - 1e-9))
        n = max(3, n + (1 - n % 2))  # odd, so that a cell centre sits at the midpoint
        dx = L / n
        off[s], n_of[s], dx_of[s] = len(cA0), n, dx
        ri, ro = inp[f"r0in_{s}"], inp[f"r0out_{s}"]
        ci, co = inp[f"c0in_{s}"], inp[f"c0out_{s}"]

        def par(xi):
            r = ri + (ro - ri) * xi
            c = ci + (co - ci) * xi
            a0 = math.pi * r * r
            return a0, 2 * rho * c * c * math.sqrt(a0)

        for i in range(n):
            a0, b = par((i + 0.5) / n)
            cA0.append(a0)
            cb.append(b)
            cG.append(inp[f"Gamma_{s}"])
            cdx.append(dx)
        for i in range(n + 1):
            a0, b = par(i / n)
            fA0.append(a0)
            fb.append(b)
    net.off, net.n, net.dx = off, n_of, dx_of
    net.cA0, net.cb, net.cG, net.cdx = map(np.array, (cA0, cb, cG, cdx))
    net.fA0, net.fb = np.array(fA0), np.array(fb)
    nc = len(cA0)
    net.nc = nc
    # face f of segment s: index foff[s] + i, i = 0..n; cells either side
    foff, k = {}, 0
    for s in range(1, N_SEG + 1):
        foff[s] = k
        k += n_of[s] + 1
    net.foff = foff
    # interior faces: left cell, right cell, face index
    il, ir, ifc = [], [], []
    for s in range(1, N_SEG + 1):
        for i in range(1, n_of[s]):
            il.append(off[s] + i - 1)
            ir.append(off[s] + i)
            ifc.append(foff[s] + i)
    net.il, net.ir, net.ifc = np.array(il), np.array(ir), np.array(ifc)
    # each cell: its left and right face
    lf, rf = [], []
    for s in range(1, N_SEG + 1):
        for i in range(n_of[s]):
            lf.append(foff[s] + i)
            rf.append(foff[s] + i + 1)
    net.lf, net.rf = np.array(lf), np.array(rf)
    # neighbours for slopes (within the segment; an end cell uses its one neighbour)
    lo, hi = [], []
    for s in range(1, N_SEG + 1):
        for i in range(n_of[s]):
            lo.append(off[s] + max(i - 1, 0))
            hi.append(off[s] + min(i + 1, n_of[s] - 1))
    net.lo, net.hi = np.array(lo), np.array(hi)
    return net


def _simulate(inp, st):
    rho, mu = inp["rho"], inp["mu"]
    pext, pout = inp["Pext"], inp["Pout"]
    T = inp["T"]
    visc = bool(st["viscoelastic"])
    net = _build(inp, st)
    dt = st["dt_dx"] * st["dx"]
    n_per = int(round(T / dt))
    dt = T / n_per
    cA0, cb = net.cA0, net.cb
    fA0, fb = net.fA0, net.fb
    csq0, fsq0 = np.sqrt(cA0), np.sqrt(fA0)
    ck = np.sqrt(cb / (2 * rho * cA0))  # c = k A^(1/4)
    fk = np.sqrt(fb / (2 * rho * fA0))
    fc0 = fk * fA0 ** 0.25
    lf, rf, lo, hi = net.lf, net.rf, net.lo, net.hi
    il, ir, ifc = net.il, net.ir, net.ifc
    cdx = net.cdx
    kfric = -22.0 * math.pi * mu / rho

    def p_of(a, b, a0, sq0):
        return pext + b / a0 * (np.sqrt(a) - sq0)

    def a_of(p, b, a0, sq0):
        return (sq0 + (p - pext) * a0 / b) ** 2

    A = cA0.copy()
    U = np.zeros(net.nc)

    # segment ends: the end cell, its face, and the direction of the outgoing invariant
    seg_in_cell = np.array([net.off[s] for s in range(1, N_SEG + 1)])
    seg_out_cell = np.array([net.off[s] + net.n[s] - 1 for s in range(1, N_SEG + 1)])
    seg_in_face = np.array([net.foff[s] for s in range(1, N_SEG + 1)])
    seg_out_face = np.array([net.foff[s] + net.n[s] for s in range(1, N_SEG + 1)])
    groups = {}
    for p, ds in sorted(TREE.items()):
        groups.setdefault(len(ds) + 1, []).append((p, ds))
    jinfo = []
    for k, items in sorted(groups.items()):
        faces = np.array([[seg_out_face[p - 1]] + [seg_in_face[d - 1] for d in ds] for p, ds in items])
        cells = np.array([[seg_out_cell[p - 1]] + [seg_in_cell[d - 1] for d in ds] for p, ds in items])
        sign = np.array([[1.0] + [-1.0] * (k - 1) for _ in items])  # +1: outlet end (forward invariant)
        jinfo.append((k, faces, cells, sign))
    t_faces = np.array([seg_out_face[s - 1] for s in TERMINALS])
    t_cells = np.array([seg_out_cell[s - 1] for s in TERMINALS])
    Rp = np.array([inp[f"Rp_{s}"] for s in TERMINALS])
    in_face, in_cell = seg_in_face[0], seg_in_cell[0]
    n_iter = int(st["newton_iter"])

    nf = len(fA0)
    # visco-elastic implicit step: interior faces only
    if visc:
        Gf = np.zeros(nf)
        Gf[ifc] = 0.5 * (net.cG[il] + net.cG[ir])

    ncyc = int(st["n_cycles"])
    rec_every = max(1, int(round(st["sample_dt"] / dt)))
    nrec = n_per // rec_every
    rec_A = np.zeros((nrec, net.nc))
    rec_U = np.zeros((nrec, net.nc))
    cfl = 0.0
    t = 0.0
    for cyc in range(ncyc):
        last = cyc == ncyc - 1
        for step in range(n_per):
            P = p_of(A, cb, cA0, csq0)
            c = ck * A ** 0.25
            cfl = max(cfl, float(np.max((np.abs(U) + c) * dt / cdx)))
            # limited slopes of P and U within each segment
            dPm, dPp = P - P[lo], P[hi] - P
            dUm, dUp = U - U[lo], U[hi] - U
            end = (lo == np.arange(net.nc)) | (hi == np.arange(net.nc))
            sP = np.where(end, dPm + dPp, _minmod(dPm, dPp))
            sU = np.where(end, dUm + dUp, _minmod(dUm, dUp))
            PL, PR = P - 0.5 * sP, P + 0.5 * sP  # at the cell's left and right faces
            UL, UR = U - 0.5 * sU, U + 0.5 * sU
            AL = a_of(PL, fb[lf], fA0[lf], fsq0[lf])
            AR = a_of(PR, fb[rf], fA0[rf], fsq0[rf])
            # Hancock predictor: half a step, from the flux difference across the cell
            dQ = AR * UR - AL * UL
            dF2 = 0.5 * (UR * UR - UL * UL) + (PR - PL) / rho
            PA = cb / cA0 / (2 * np.sqrt(A))  # dP/dA
            dP_h = -0.5 * dt / cdx * PA * dQ
            dU_h = -0.5 * dt / cdx * dF2 + 0.5 * dt * kfric * U / A
            PL, PR = PL + dP_h, PR + dP_h
            UL, UR = UL + dU_h, UR + dU_h
            AL = a_of(PL, fb[lf], fA0[lf], fsq0[lf])
            AR = a_of(PR, fb[rf], fA0[rf], fsq0[rf])
            # each face: the state just left of it (cell's right) and just right of it (cell's left)
            Af = np.zeros(nf)
            Uf = np.zeros(nf)
            # interior faces: upwinding through the Riemann invariants
            aL, uL = AR[il], UR[il]
            aR, uR = AL[ir], UL[ir]
            kf, c0f = fk[ifc], fc0[ifc]
            W1 = uL + 4 * (kf * aL ** 0.25 - c0f)
            W2 = uR - 4 * (kf * aR ** 0.25 - c0f)
            Af[ifc] = (((W1 - W2) / 8 + c0f) / kf) ** 4
            Uf[ifc] = 0.5 * (W1 + W2)
            # outgoing invariants at the segment ends
            Wout = UR[seg_out_cell] + 4 * (fk[seg_out_face] * AR[seg_out_cell] ** 0.25 - fc0[seg_out_face])
            Win = UL[seg_in_cell] - 4 * (fk[seg_in_face] * AL[seg_in_cell] ** 0.25 - fc0[seg_in_face])
            th = t + 0.5 * dt
            # inlet: A U = Qin
            q = _inflow(inp, th)
            k0 = in_face
            a, w = AL[in_cell], Win[0]
            for _ in range(n_iter):
                cc = fk[k0] * a ** 0.25
                u = w + 4 * (cc - fc0[k0])
                a = a - (a * u - q) / (u + cc)
            Af[k0], Uf[k0] = a, w + 4 * (fk[k0] * a ** 0.25 - fc0[k0])
            # terminals: A U = (P - Pout)/Rp
            fi = t_faces
            a = AR[t_cells].copy()
            w = Wout[np.array(TERMINALS) - 1]
            bb, a0, s0 = fb[fi] / fA0[fi], fA0[fi], fsq0[fi]
            for _ in range(n_iter):
                cc = fk[fi] * a ** 0.25
                u = w - 4 * (cc - fc0[fi])
                p = pext + bb * (np.sqrt(a) - s0)
                g = a * u - (p - pout) / Rp
                dg = u - cc - bb / (2 * np.sqrt(a)) / Rp
                a = a - g / dg
            Af[fi], Uf[fi] = a, w - 4 * (fk[fi] * a ** 0.25 - fc0[fi])
            # junctions: mass conserved, total pressure continuous
            for k, faces, cells, sign in jinfo:
                a = np.where(sign > 0, AR[cells], AL[cells])
                segs_w = np.where(sign > 0, Wout[_seg_of(net, faces, sign)], Win[_seg_of(net, faces, sign)])
                kk, c0n = fk[faces], fc0[faces]
                bb, s0 = fb[faces] / fA0[faces], fsq0[faces]
                nj = faces.shape[0]
                for _ in range(n_iter):
                    cc = kk * a ** 0.25
                    u = segs_w - sign * 4 * (cc - c0n)
                    du = -sign * cc / a
                    dp = bb / (2 * np.sqrt(a))
                    pt = bb * (np.sqrt(a) - s0) + 0.5 * rho * u * u
                    dpt = dp + rho * u * du
                    res = np.zeros((nj, k))
                    jac = np.zeros((nj, k, k))
                    res[:, 0] = np.sum(sign * a * u, axis=1)
                    jac[:, 0, :] = sign * (u + a * du)
                    for m in range(1, k):
                        res[:, m] = pt[:, 0] - pt[:, m]
                        jac[:, m, 0] = dpt[:, 0]
                        jac[:, m, m] = -dpt[:, m]
                    a = a - np.linalg.solve(jac, res[..., None])[..., 0]
                Af[faces] = a
                Uf[faces] = segs_w - sign * 4 * (kk * a ** 0.25 - c0n)
            # conservative update
            F1 = Af * Uf
            F2 = 0.5 * Uf * Uf + (pext + fb / fA0 * (np.sqrt(np.where(Af > 0, Af, fA0)) - fsq0)) / rho
            Uh = 0.5 * (UL + UR)
            Ah = 0.5 * (AL + AR)
            A = A - dt / cdx * (F1[rf] - F1[lf])
            U = U - dt / cdx * (F2[rf] - F2[lf]) + dt * kfric * Uh / Ah
            if visc:
                # U - dt/dx [kappa (dQ/dx)]_faces = U*, kappa = Gamma/(rho A0 sqrt(A)) at interior faces
                kap = np.zeros(nf)
                Afc = 0.5 * (A[il] + A[ir])
                kap[ifc] = Gf[ifc] / (rho * fA0[ifc] * np.sqrt(Afc))
                dxf = 0.5 * (cdx[il] + cdx[ir])
                gr = np.zeros(nf)
                gr[ifc] = kap[ifc] / dxf  # flux = -kap (Q_r - Q_l)/dxf
                wl = dt / cdx * gr[lf]
                wr = dt / cdx * gr[rf]
                ab = np.zeros((3, net.nc))
                ab[1] = 1.0 + (wl + wr) * A
                ab[0, 1:] = -wr[:-1] * A[1:]  # row i, column i+1
                ab[2, :-1] = -wl[1:] * A[:-1]  # row i, column i-1
                U = solve_banded((1, 1), ab, U)
            t += dt
            if last and (step + 1) % rec_every == 0:
                j = (step + 1) // rec_every - 1
                if j < nrec:
                    rec_A[j] = A
                    rec_U[j] = U
        if not (np.all(np.isfinite(A)) and np.all(A > 0)):
            raise FloatingPointError("the simulation diverged")
    return {"net": net, "A": rec_A, "U": rec_U, "dt_rec": rec_every * dt, "cfl": cfl}


def _seg_of(net, faces, sign):
    """Segment index (0-based) of each junction face."""
    if not hasattr(net, "_face_seg"):
        fs = {}
        for s in range(1, N_SEG + 1):
            fs[net.foff[s]] = s - 1
            fs[net.foff[s] + net.n[s]] = s - 1
        net._face_seg = fs
    return np.vectorize(net._face_seg.get)(faces)


def _key(inputs, settings):
    return (tuple(sorted((k, v) for k, v in inputs.items() if k != "t_cycle")),
            tuple(sorted((k, str(v)) for k, v in settings.items())))


def _mid(net, s):
    return net.off[s] + net.n[s] // 2


def run(inputs, settings):
    key = _key(inputs, settings)
    if key not in _MEMO:
        _MEMO.clear()
        _MEMO[key] = _simulate(inputs, settings)
    sim = _MEMO[key]
    net, RA, RU = sim["net"], sim["A"], sim["U"]
    nrec = RA.shape[0]
    # sample j is at (j + 1) * dt_rec into the last cycle; periodic linear interpolation
    pos = (inputs["t_cycle"] % inputs["T"]) / sim["dt_rec"] - 1.0
    j0 = int(math.floor(pos)) % nrec
    j1 = (j0 + 1) % nrec
    w = pos - math.floor(pos)
    out = {}
    for s in SITES:
        k = _mid(net, s)
        a = (1 - w) * RA[j0, k] + w * RA[j1, k]
        u = (1 - w) * RU[j0, k] + w * RU[j1, k]
        out[f"P_mid_{s}"] = inputs["Pext"] + net.cb[k] / net.cA0[k] * (math.sqrt(a) - math.sqrt(net.cA0[k]))
        out[f"Q_mid_{s}"] = a * u
    # ascending aorta: the largest change in diameter over the cycle, relative to the mean diameter
    a, b = net.off[1], net.off[1] + net.n[1]
    D = np.sqrt(RA[:, a:b])
    out["dD_asc"] = float(np.max((D.max(axis=0) - D.min(axis=0)) / D.mean(axis=0))) * 100.0
    return out
