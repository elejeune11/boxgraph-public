# Port to Python of Supplementary Software 1 of Andreu et al. 2021: cmstretchg.m (lines 50-191), with the
# scaling of its output in stretchscriptg.m (lines 54, 56). Our code, not the authors': it follows their
# lines one by one. The rate tables it reads (kofflr.mat) are rebuilt by the port of 'loading rate
# script.m' in ../lr_rate_port (built_from), which reproduces the shipped tables cell by cell.
# Units as in the MATLAB code: N, m, s; densities per um^2. No I/O.
import bisect
import importlib.util
import math
import os
import random

import numpy as np


def _lr():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lr_rate_port", "model.py")
    spec = importlib.util.spec_from_file_location("andreu2021_code_lr_rate_port", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tables(inputs, settings):
    """kofflr.mat: kint, kunf over (loading rate, starting force), the grid L, and the index from which
    kact is inf ('loading rate script.m' lines 63-67)."""
    lr = _lr()
    f, fstart, L, step, steps = lr.grids(settings)
    p_floor = float(settings["p_floor"])
    # the tables are made by 'loading rate script.m' with its own constants (lines 10-11, 28-29, 63)
    k_int = lr.rate_on_grid("koff", inputs, f)
    k_unf = lr.rate_on_grid("kunf", {"ln_kunf0": inputs["ln_kunf0_table"], "kunf_b": inputs["kunf_b_table"],
                                     "pt": inputs["pt_table"]}, f)
    kint = [list(lr.corrected_row(k_int, f, Lj, fstart, step, steps, p_floor)) for Lj in L]
    kunf = [list(lr.corrected_row(k_unf, f, Lj, fstart, step, steps, p_floor)) for Lj in L]
    ibreak = int(np.argmin(np.abs(fstart - inputs["Fbreaking"])))  # line 66 (first minimum)
    return kint, kunf, list(L), ibreak, len(fstart), lr


def _nearest(Lk, x):
    """[trash, indL] = min(abs(L - Lk)) (cmstretchg.m line 88): first index of the minimum."""
    i = bisect.bisect_left(Lk, x)
    if i == 0:
        return 0
    if i >= len(Lk):
        return len(Lk) - 1
    return i - 1 if abs(x - Lk[i - 1]) <= abs(x - Lk[i]) else i


def simulate(inputs, settings):
    kint, kunf, Lk, ibreak, nfs, lr = _tables(inputs, settings)
    cm = {"a": inputs["cm_a"], "b": inputs["cm_b"], "c": inputs["cm_c"], "d": inputs["cm_d"],
          "g": inputs["cm_g"], "fend": inputs["cm_fend"]}
    rng = random.Random(int(settings["seed"]))
    A, fr = inputs["A"], inputs["fr"]
    nc = int(round(inputs["nc"]))
    kont1, kc, ksub, pt = inputs["kont1"], inputs["kc"], inputs["ksub"], inputs["pt"]
    mr, intadd = inputs["mr"], inputs["intadd"]
    kuf0, kufb = math.exp(inputs["ln_kunf0"]), inputs["kunf_b"]
    kf0, kfb = math.exp(inputs["ln_kfold0"]), inputs["kfold_b"]
    t_total = float(settings["t_total"])

    dint1i = inputs["dint1"]
    dint1 = dint1i
    # State of the bound clutches only: slot index (1..nc in the code), position xc, folding status.
    # Every unbound clutch sits at xsub with zero force and folding 0 (lines 137-138, 147-148, 165).
    slots, xc, unf = [], [], []
    free = list(range(nc))
    xsub = 0.0
    t_end = 0.0
    first = True
    prev = None  # (t, f, v, nb, dint) of the previous step, for the time averages of lines 188-191
    acc_f = acc_v = acc_nb = acc_d = 0.0

    while t_end < t_total:  # line 63
        s = math.sin(2 * math.pi * fr * t_end)
        vf = 1e-6 * 2 * A * fr * (1.0 if s > 0 else (-1.0 if s < 0 else 0.0))  # line 69, 'tr'
        nb = len(slots)
        L = 0.0 if nb == 0 else abs(vf) * ksub / nb  # lines 79-83
        jL = _nearest(Lk, L)
        rowi, rowu = kint[jL], kunf[jL]

        # Lines 87-125: rates of each bound clutch, then a waiting time for every possible event.
        best_t, best_type, best_k = math.inf, -1, -1
        breaking = []  # clutches whose breaking time is zero (kbr = inf, folded): ties go to the lowest slot
        times = []
        for k in range(nb):
            Fa = abs(kc * (xc[k] - xsub))  # line 180
            indf = math.floor(Fa * 1e12 + 0.5)  # line 87 (round half away from zero), 0-based
            if indf + 1 > nfs:  # lines 89, 103-105
                koff1 = float(lr.koffcb(Fa, "cm", cm))
                kuf = kuf0 * math.exp(min(kufb * Fa * pt, 700.0))
                kbr = math.inf
            else:
                koff1, kuf = rowi[indf], rowu[indf]
                kbr = math.inf if indf >= ibreak else 0.0
            folded = not unf[k]
            if folded and kbr == math.inf:
                breaking.append(k)
                continue
            # unbinding (type 0); unfolding (2) if folded; refolding (3) if unfolded (line 97)
            tub = -math.log(1.0 - rng.random()) / koff1 if koff1 > 0 else math.inf
            times.append((tub, 0, k))
            if folded:
                tuf = -math.log(1.0 - rng.random()) / kuf if kuf > 0 else math.inf
                times.append((tuf, 2, k))
            else:
                kf = kf0 * math.exp(kfb * Fa * pt)
                tf = -math.log(1.0 - rng.random()) / kf if kf > 0 else math.inf
                times.append((tf, 3, k))
        if breaking:
            k = min(breaking, key=lambda q: slots[q])
            best_t, best_type, best_k = 0.0, 4, k
        else:
            for tt, ty, k in times:
                if tt < best_t:
                    best_t, best_type, best_k = tt, ty, k
            m = len(free)
            if m:
                # The binding times of the m unbound clutches (line 122) are m independent exponentials of
                # rate kont1*dint1: their minimum is one exponential of rate m*kont1*dint1, at a clutch
                # chosen uniformly among them.
                tb = -math.log(1.0 - rng.random()) / (m * kont1 * dint1)
                if tb < best_t:
                    best_t, best_type, best_k = tb, 1, -1
        ti = best_t
        if ti == math.inf:
            ti = t_total  # no event can happen: nothing changes until the end

        # Lines 134-150: execute the event.
        if best_type == 0:
            k = best_k
            dint1 = dint1 - intadd * (1 - (1 if unf[k] else 0))
            free.append(slots.pop(k))
            xc.pop(k)
            unf.pop(k)
        elif best_type == 1:
            slot = free.pop(rng.randrange(len(free)))
            slots.append(slot)
            xc.append(xsub)
            unf.append(False)
        elif best_type == 2:
            unf[best_k] = True
            dint1 = dint1 + intadd
        elif best_type == 3:
            unf[best_k] = False
        elif best_type == 4:
            k = best_k
            free.append(slots.pop(k))
            xc.pop(k)
            unf.pop(k)
            dint1 = dint1 - intadd
        # lines 153-157
        if dint1 < dint1i:
            dint1 = dint1i
        elif dint1 > mr:
            dint1 = mr

        # Lines 163-167: move the bound clutches, force balance on the substrate.
        nb = len(slots)
        for k in range(nb):
            xc[k] += vf * ti
        xsub = kc * sum(xc) / (ksub + nb * kc)
        f_now = xsub * ksub

        # Lines 171-177 (time vector, density record) and 188-191 (time averages, accumulated as we go)
        if first:
            t_new = ti
            d_now = dint1i
            first = False
        else:
            t_new = t_end + ti
            d_now = dint1
        if prev is not None:
            dt = t_new - prev[0]
            acc_f += prev[1] * dt
            acc_v += prev[2] * dt
            acc_nb += prev[3] * dt
            acc_d += prev[4] * dt
        prev = (t_new, f_now, vf, nb, d_now)
        t_end = t_new

    return acc_f / t_end, acc_v / t_end, acc_nb / t_end, acc_d / t_end


def run(inputs, settings):
    mf, mv, mnb1, mdint1 = simulate(inputs, settings)
    yap = inputs["bl"] + (mdint1 / inputs["dint1"] - 1) * inputs["sc"]  # stretchscriptg.m line 54
    P = mf / (3.14159 * inputs["a"] ** 2)  # line 56
    length = (yap - inputs["yap_at_zero_length"]) * inputs["length_per_yap"]
    return {"mdint1": mdint1, "yap_scaled": yap, "adhesion_length": length, "mf": mf, "P": P, "mnb1": mnb1}
