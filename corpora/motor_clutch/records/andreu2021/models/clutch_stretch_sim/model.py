# Stochastic clutch model under imposed cyclic stretch (Andreu et al. 2021, Methods pp. 10-11).
# Units inside: pN, nm, s, um^-2. No I/O.
import math

import numpy as np


def _corrected_table(k_of_f, L_grid, f_grid, fstart, p_floor):
    """Eqs. 5-6: for each loading rate L and baseline force Fb, the corrected rate
    k'(Fb, L) = 1 / <lifetime>, where force ramps from Fb at rate L.
    p(F, L) = k(F)/L exp(-1/L int_0^F k dF), truncated to F >= Fb and renormalised;
    Fm = int F p dF; lifetime = (Fm - Fb)/L (reduces to Fm/L for Fb = 0)."""
    df = f_grid[1] - f_grid[0]
    k = k_of_f(f_grid)
    # cumulative trapezoid of k from 0 to F
    cum = np.concatenate([[0.0], np.cumsum((k[1:] + k[:-1]) * 0.5 * df)])
    i_start = np.rint(fstart / df).astype(int)
    out = np.empty((len(L_grid), len(fstart)))
    for j, L in enumerate(L_grid):
        p = k / L * np.exp(-cum / L)
        # tail integrals by trapezoid from index i to the end
        w = p.copy()
        fw = f_grid * p
        seg_p = (w[1:] + w[:-1]) * 0.5 * df
        seg_fp = (fw[1:] + fw[:-1]) * 0.5 * df
        tail_p = np.concatenate([np.cumsum(seg_p[::-1])[::-1], [0.0]])
        tail_fp = np.concatenate([np.cumsum(seg_fp[::-1])[::-1], [0.0]])
        for i, ii in enumerate(i_start):
            if p[ii] < p_floor or tail_p[ii] <= 0.0:
                out[j, i] = k[ii]  # density vanishes: the event would be at constant force
            else:
                fm = tail_fp[ii] / tail_p[ii]
                life = (fm - fstart[i]) / L
                out[j, i] = 1.0 / life if life > 0 else k[ii]
    return out


def _tables(inputs, settings):
    a1, b1, a2, b2 = inputs["koff_a"], inputs["koff_b"], inputs["koff_c"], inputs["koff_d"]
    ln_ku0, bu, FR = inputs["ln_kunf0"], inputs["kunf_b"], inputs["FR"]

    cap = 575.0  # exponent cap (~1e250 /s): such rates are instantaneous either way, and sums stay finite

    def koff(f):
        return a1 * np.exp(np.minimum(b1 * f, cap)) + a2 * np.exp(np.minimum(b2 * f, cap))

    def kunf(f):
        return np.exp(np.minimum(ln_ku0 + bu * FR * f, cap))

    df = float(settings["df"])
    f_grid = np.arange(0.0, float(settings["f_max"]) + df / 2, df)
    fstart = np.arange(0.0, float(settings["fstart_max"]) + 0.5, float(settings["dfstart"]))
    L_grid = float(settings["L_min"]) * 2.0 ** np.arange(0.0, float(settings["L_octaves"]) + 1e-9, 0.5)
    p_floor = float(settings["p_floor"])
    return (koff, kunf, L_grid, fstart,
            _corrected_table(koff, L_grid, f_grid, fstart, p_floor),
            _corrected_table(kunf, L_grid, f_grid, fstart, p_floor))


def simulate(inputs, settings):
    koff, kunf, L_grid, fstart, T_off, T_unf = _tables(inputs, settings)
    dfs = fstart[1] - fstart[0]
    nfs = len(fstart)
    rng = np.random.default_rng(int(settings["seed"]))

    A_nm = inputs["A"] * 1e3            # um -> nm
    fr = inputs["fr"]
    nf = int(round(inputs["nf"]))
    kon_i = inputs["kon_i"]             # um^2/s
    kc, ksub = inputs["kc"], inputs["ksub"]   # pN/nm
    dmin, dmax, dadd = inputs["dmin"], inputs["dmax"], inputs["dadd"]
    Fact = inputs["Fact"]
    i_act = int(round(Fact / dfs))      # first grid index at which actin breaks
    t_total = float(settings["t_total"])

    # state: bound clutches only (unbound ones all sit at the substrate position)
    xc = np.zeros(0)        # positions of bound clutches (nm)
    unf = np.zeros(0, bool)  # talin unfolded
    xsub = 0.0
    dint = dmin
    t = 0.0
    acc_d = 0.0             # integral of dint dt
    n_events = 0
    vmag = 2.0 * A_nm * fr  # |v| = 2 A f

    while t < t_total:
        s = math.sin(2.0 * math.pi * fr * t)
        v = vmag * (1.0 if s > 0 else (-1.0 if s < 0 else 0.0))
        nb = len(xc)
        F = kc * (xc - xsub)
        Fa = np.abs(F)
        idx = np.rint(Fa / dfs).astype(int)
        if nb:
            L = abs(v) * ksub / nb
        else:
            L = 0.0
        jL = int(np.argmin(np.abs(L - L_grid)))
        high = idx >= nfs
        idc = np.where(high, 0, idx)
        k_off = T_off[jL, idc]
        k_unf = T_unf[jL, idc]
        if high.any():
            k_off = np.where(high, koff(Fa), k_off)
            k_unf = np.where(high, kunf(Fa), k_unf)
        folded = ~unf
        breaking = folded & (idx >= i_act)
        if breaking.any():
            # actin breaks instantaneously above Fact: zero waiting time
            i = int(np.flatnonzero(breaking)[0])
            dt = 0.0
            xc = np.delete(xc, i)
            unf = np.delete(unf, i)
            dint -= dadd
        else:
            r_unbind = k_off
            r_unf = np.where(folded, k_unf, 0.0)
            r_bind = (nf - nb) * kon_i * dint
            tot = r_unbind.sum() + r_unf.sum() + r_bind
            dt = -math.log(rng.random()) / tot
            if t + dt > t_total:
                acc_d += dint * (t_total - t)
                t = t_total
                break
            acc_d += dint * dt   # density held over the waiting time, before the event
            u = rng.random() * tot
            if u < r_bind:
                xc = np.append(xc, xsub)
                unf = np.append(unf, False)
            else:
                u -= r_bind
                c1 = np.cumsum(r_unbind)
                if u < c1[-1]:
                    i = min(int(np.searchsorted(c1, u, side="right")), nb - 1)
                    if not unf[i]:
                        dint -= dadd
                    xc = np.delete(xc, i)
                    unf = np.delete(unf, i)
                else:
                    u -= c1[-1]
                    c2 = np.cumsum(r_unf)
                    i = min(int(np.searchsorted(c2, u, side="right")), nb - 1)
                    unf[i] = True
                    dint += dadd
        dint = min(max(dint, dmin), dmax)
        t += dt
        n_events += 1
        # end of step: bound clutches move with the actin, substrate by force balance (Eq. 4)
        xc = xc + v * dt
        nb = len(xc)
        xsub = kc * xc.sum() / (ksub + nb * kc)
    return acc_d / t_total, n_events


def run(inputs, settings):
    d_mean, n_events = simulate(inputs, settings)
    length = inputs["len0"] + inputs["len_scale"] * (d_mean / inputs["dmin"] - 1.0)
    return {"d_mean": d_mean, "adhesion_length": length}
