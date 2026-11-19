# Reader's stand-in for the paper's unstated step from Fig. 4 to h/h0 = 2.0 +/- 0.1 at onset:
# the mid-point between the most swollen gel that stayed flat and the least swollen gel that creased.


def run(inputs, settings):
    return {"h_ratio": 0.5 * (max(inputs["flat"]["y"]) + min(inputs["creased"]["y"]))}
