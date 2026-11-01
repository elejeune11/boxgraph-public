"""Lifetime of a slip bond under force (a stand-in for an author's code)."""
import math

K0 = 0.5  # unloaded off-rate, 1/s
XB = 0.5   # bond length, nm


def lifetime(F, kT=4.1):
    return 1 / K0 * math.exp(-F * XB / kT)
