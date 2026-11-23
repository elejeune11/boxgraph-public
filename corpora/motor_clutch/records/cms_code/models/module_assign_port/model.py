# Port of cms2Dv1_0.m lines 236-240 (our code). MATLAB's ceil is math.ceil; both work on IEEE doubles,
# so the product maxm*(1-totm/mpool) rounds up the same way here as in the code.
import math


def run(inputs, settings):
    maxm, totm, mpool = inputs["maxm"], inputs["totm"], inputs["mpool"]
    if totm < mpool:
        nm = math.ceil(maxm * (1 - totm / mpool))
    else:
        nm = 1
    return {"nm": float(nm)}
