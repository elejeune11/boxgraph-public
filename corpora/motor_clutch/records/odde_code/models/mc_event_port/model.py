# Port to Python of the event-stepping motor-clutch loop of motorclutch2_3.m (lines 42-155, one
# stiffness, i.e. one pass of the jj loop), which is also the loop of motorclutch1_1.m (lines 41-120).
# Our code, written line by line from the MATLAB; it holds no values of its own: every parameter is an
# input, in the code's own units and sign convention (vu, Fm, Fb negative; positions negative).
# MATLAB's random stream cannot be reproduced: rand() is numpy's, seeded.
import numpy as np


def simulate(inputs, settings):
    nm = inputs["nm"]
    Fm = inputs["Fm"]
    vu = inputs["vu"]
    nc = int(round(inputs["nc"]))
    kon = inputs["kon"]
    koff = inputs["koff"]
    Fb = inputs["Fb"]
    Kc = inputs["Kc"]
    gain = inputs["gain"]
    Ksub = inputs["Ksub"]
    events = int(settings.get("events", 100000))
    dt0 = float(settings.get("dt_initial", 0.005))
    ts0 = float(settings.get("timestep_initial", 0.0))
    rng = np.random.default_rng(int(settings.get("seed", 1)))

    n = events + 1
    cstate = np.zeros(nc, dtype=bool)          # line 47
    xc = np.zeros(nc)                          # line 50
    t = np.zeros(n)                            # lines 51-59
    subpos = np.zeros(n)
    numcon = np.zeros(n)
    vel = np.zeros(n)
    timestep = np.zeros(n)
    cough = np.zeros(n)
    Ft = np.zeros(n)
    totFc = np.zeros(n)

    # initial state, lines 62-77
    ceng = np.flatnonzero(cstate)
    cdisen = np.flatnonzero(~cstate)
    vf = vu
    xc[ceng] = xc[ceng] + vf * dt0
    xsub = Kc * np.sum(xc[ceng]) / (Ksub + len(ceng) * Kc)
    xc[cdisen] = xsub
    Fc = Kc * (xc - xsub)
    t[0] = 0.0
    subpos[0] = xsub
    numcon[0] = len(ceng)
    vel[0] = -vf
    timestep[0] = ts0

    # event stepping, lines 80-141
    for i in range(1, n):
        if len(cdisen) == 0:                                   # lines 84-88
            dtbind = np.inf
        else:
            tbind = -np.log(rng.random(len(cdisen))) / kon
            indbind = int(np.argmin(tbind))
            dtbind = tbind[indbind]
        if len(ceng) == 0:                                     # lines 91-99
            dtunbind = np.inf
            cough[i] = koff
            totFc[i] = 0.0
        else:
            Fe = Fc[ceng]
            rate = koff * np.exp(Fe / (Fb + gain * Fe))
            tunbind = -np.log(rng.random(len(ceng))) / rate
            indunbind = int(np.argmin(tunbind))
            dtunbind = tunbind[indunbind]
            cough[i] = np.mean(rate)
            totFc[i] = np.mean(Fe)
        if dtbind < dtunbind:                                  # lines 104-115
            cstate[cdisen[indbind]] = True
            dt = dtbind
        else:
            cstate[ceng[indunbind]] = False
            dt = dtunbind

        ceng = np.flatnonzero(cstate)                          # lines 117-128
        cdisen = np.flatnonzero(~cstate)
        Ftrac = Ksub * xsub
        vf = vu * (1 - ((Ksub * xsub) / (nm * Fm)))
        xc[ceng] = xc[ceng] + vf * dt
        xsub = Kc * np.sum(xc[ceng]) / (Ksub + len(ceng) * Kc)
        xc[cdisen] = xsub
        Fc = Kc * (xc - xsub)

        t[i] = t[i - 1] + dt                                   # lines 134-140
        subpos[i] = xsub
        numcon[i] = len(ceng)
        vel[i] = -vf
        timestep[i] = dt
        Ft[i] = Ftrac

    return t, subpos, numcon, vel, timestep, cough, Ft, totFc


def run(inputs, settings):
    t, subpos, numcon, vel, timestep, cough, Ft, totFc = simulate(inputs, settings)
    T = t[-1]
    cyctime = np.diff(t[subpos == 0])                          # line 142
    retro = np.sum((vel * timestep) / T)                       # line 144
    failures = len(numcon[numcon == 0]) - 1                    # line 152
    failfreq = failures / T                                    # line 145
    avnumcon = np.sum((numcon * timestep) / T)                 # line 146
    avtrac = np.sum((Ft * timestep) / T)                       # line 149
    avFc = np.sum((totFc * timestep) / T)                      # line 151
    cyct = float(np.mean(cyctime)) if len(cyctime) else float("nan")   # line 153
    return {
        "v_retro": float(retro),
        "F_trac": float(-avtrac),       # plotted as -avtrac, line 164
        "fail_freq": float(failfreq),
        "t_cycle": cyct,
        "n_eng": float(avnumcon),
        "k_ens": float(inputs["Kc"] * avnumcon),   # not in the code: Bangasser 2013's definition (p. 7)
        "Fc_mean": float(-avFc),        # mean engaged-clutch tension, sign turned to tension positive
        "t_total": float(T),
    }
