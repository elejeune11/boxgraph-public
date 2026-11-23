"""What each reading of panzetta2023 reads: the panel's printed axis labels, the series' grey band
and where to start following it. Keyed by reading id (the stub's file name). The reading method is
in _p23.py."""

LOG_10_1000 = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
LOG_10_200 = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200]

_X_NC = {"scale": "log10", "ticks": LOG_10_1000, "anchor": "left", "anchor_value": 10}
_Y_70_110 = {"ticks": [70, 75, 80, 85, 90, 95, 100, 105, 110], "anchor": "bottom", "anchor_value": 70}
_Y_70_110_TOP = {"ticks": [70, 75, 80, 85, 90, 95, 100, 105, 110], "anchor": "top", "anchor_value": 110}

BLACK = (0, 80)
GREY4 = (95, 175)

SPECS = {
    # ---- Fig. 4 (p. 6): canonical (grey solid) and modified (black dashed), ks = 1 pN/nm
    "fig4a_canonical": {"kind": "matlab", "x": _X_NC, "y": _Y_70_110, "band": GREY4, "exclude": (0, 80, 3),
                        "seeds": [{"x": 300, "rank": -1, "min_half": 2.5}], "max_gap": 80},
    "fig4a_modified": {"kind": "matlab", "x": _X_NC, "y": _Y_70_110, "band": BLACK,
                       "seeds": [{"x": 600, "rank": -1, "min_half": 2.5, "ymax": 90}],
                       "max_gap": 60, "bend": 1.0},
    # Fig. 4B also has minor y ticks: only the longer, labelled ticks are taken (tick_len 14)
    "fig4b_canonical": {"kind": "matlab", "x": _X_NC, "y": _Y_70_110, "band": GREY4, "exclude": (0, 80, 3),
                        "y_tick_len": 14, "seeds": [{"x": 400, "rank": -1, "min_half": 2.5}], "max_gap": 80},
    "fig4b_modified": {"kind": "matlab", "x": _X_NC, "y": _Y_70_110, "band": BLACK, "y_tick_len": 14,
                       "seeds": [{"x": 400, "rank": -1, "min_half": 2.5, "ymax": 95}], "max_gap": 60, "bend": 1.0},
}

# ---- Fig. 5 (p. 6): seven strains, grey levels from black (0, 0.1) to the lightest (2, 3).
# The curves cross between nc of about 35 and 100; each is read on the left and on the right of
# that tangle, from a seed on each side (the seed window, in axis values, only says where to start).
_X5A = {"scale": "log10", "ticks": LOG_10_200, "anchor": "left", "anchor_value": 10}
_Y5A = {"ticks": [74, 76, 78, 80, 82, 84, 86, 88, 90], "anchor": "top", "anchor_value": 90}
# The grey levels of the five grey curves overlap in the image (JPEG noise, antialiasing), so
# all ink is one mask and each curve is told apart by continuity from its seed. On the left the
# curves lie in strain order (3 on top, 0 at the bottom); on the right in reverse.
INK = (0, 222)


def _five(left_near, right_near):
    seeds = [{"x": 12, "near": left_near, "min_half": 2.5, "to": 33}]
    if right_near is not None:
        seeds.append({"x": 180, "near": right_near, "min_half": 2.5, "within": 12, "from": 100})
    return {"kind": "matlab", "x": _X5A, "y": _Y5A, "band": INK, "close": 4, "seeds": seeds, "max_gap": 40, "bend": 0.6}


def _rank5a(k):
    """On the left (nc up to about 25) the seven curves lie apart, strain 3 on top: read by order."""
    return {"kind": "matlab", "x": _X5A, "y": _Y5A, "band": INK, "close": 4, "mode": "rank", "n": 7, "rank": k,
            "search": 10}


SPECS["fig5a_e0"] = _five(79.1, 80.64)   # strain 0 is followed on both sides (thin black, apart)
SPECS["fig5a_e01"] = _rank5a(5)
SPECS["fig5a_e025"] = _rank5a(4)
SPECS["fig5a_e05"] = _rank5a(3)
SPECS["fig5a_e1"] = _rank5a(2)
SPECS["fig5a_e2"] = _rank5a(1)
SPECS["fig5a_e3"] = _rank5a(0)


def _rank5b(k):
    """Fig. 5B (ks = 1 pN/nm): between nc of about 100 and 250 the seven curves lie apart,
    strain 3 on top (rightmost), strain 0 at the bottom: read by order."""
    return {"kind": "matlab", "x": _X_NC, "y": _Y_70_110, "band": INK, "close": 4, "mode": "rank", "n": 7,
            "rank": k, "search": 10, "y_tick_len": 14, "legend": {"x_from": 200, "ymax": 92}}


for _k, _e in enumerate(["e3", "e2", "e1", "e05", "e025", "e01", "e0"]):
    SPECS[f"fig5b_{_e}"] = _rank5b(_k)

# ---- Fig. 6 (p. 7): Excel chart, optimal nc against strain; grey (ks = 0.1, left axis) and black
# (ks = 1, right axis) filled circles on smooth lines. Markers are what is left of the series' grey
# band after an opening wider than the line.
_X6 = {"labels": [0, 0.5, 1, 1.5, 2, 2.5, 3]}
SPECS["fig6_soft"] = {"kind": "excel", "mode": "markers", "x": _X6,
                      "y": {"side": "left", "labels": [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]},
                      "band": (95, 165), "exclude": (0, 70, 2), "open_r": 9,
                      "labels": {"offset": 45, "gap": 12}, "xlabels": {"offset": 45}}
SPECS["fig6_stiff"] = {"kind": "excel", "mode": "markers", "x": _X6,
                       "y": {"side": "right", "labels": [440, 490, 540, 590, 640, 690, 740, 790]},
                       "band": (0, 70), "open_r": 9, "labels": {"offset": 45}, "xlabels": {"offset": 45}}

# ---- Fig. 3 (p. 5): Excel bar charts, canonical (light grey) and modified (dark grey; black in C)
# bars at nc = 50 and 400, with error bars (grey, lighter than the dark bars, darker than the light).
_B3 = {"kind": "excel", "mode": "bars", "min_bar": 100, "err_band": (75, 115), "cap_min": 20,
       "labels": {"offset": 8, "gap": 12, "width": 40}}
_LIGHT3, _DARK3, _BLACK3 = (145, 190), (50, 72), (0, 40)
_Y3A = {"side": "left", "labels": [0, 20, 40, 60, 80, 100, 120, 140]}
_Y3BD = {"side": "left", "labels": [-500, -450, -400, -350, -300, -250, -200, -150, -100, -50, 0]}
_Y3C = {"side": "left", "labels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
SPECS["fig3a_canonical"] = {**_B3, "y": _Y3A, "bar_band": _LIGHT3}
SPECS["fig3a_modified"] = {**_B3, "y": _Y3A, "bar_band": _DARK3}
SPECS["fig3b_canonical"] = {**_B3, "y": _Y3BD, "bar_band": _LIGHT3, "direction": 1}
SPECS["fig3b_modified"] = {**_B3, "y": _Y3BD, "bar_band": _DARK3, "direction": 1}
SPECS["fig3c_canonical"] = {**_B3, "y": _Y3C, "bar_band": _LIGHT3}
SPECS["fig3c_modified"] = {**_B3, "y": _Y3C, "bar_band": _BLACK3}
SPECS["fig3d_canonical"] = {**_B3, "y": _Y3BD, "bar_band": _LIGHT3, "direction": 1}
SPECS["fig3d_modified"] = {**_B3, "y": _Y3BD, "bar_band": _DARK3, "direction": 1}

# ---- Fig. 9 (p. 8): Excel bar charts with two y axes: dark grey bars (ks = 0.1 pN/nm, left axis)
# stand in front of light grey bars (ks = 1 pN/nm, right axis) at the same positions; a light bar is
# read only where it shows beyond the dark one. Each series has its error bar (grey, translucent
# over the dark bars): the two caps whose midpoint is the series' bar end are its error bar; a pair
# not found is left unread (no mirroring: the caps of the other series would be taken).
_B9 = {"kind": "excel", "mode": "bars", "min_bar": 100, "err_band": (75, 135), "cap_min": 20, "mirror": False,
       "pair_tol": 8, "bridge": 22, "categories": [0, 0.1, 0.25, 0.5, 1, 2, 3], "labels": {"offset": 8, "gap": 12, "width": 40}}
_DARK9, _LIGHT9 = (138, 165), (195, 228)
SPECS["fig9a_soft"] = {**_B9, "y": {"side": "left", "labels": [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]}, "bar_band": _DARK9}
SPECS["fig9a_stiff"] = {**_B9, "y": {"side": "right", "labels": [0, 50, 100, 150, 200, 250, 300, 350, 400]},
                        "bar_band": _LIGHT9, "front_band": _DARK9}
SPECS["fig9b_soft"] = {**_B9, "y": {"side": "left", "labels": [-100, -90, -80, -70, -60, -50, -40, -30, -20, -10, 0]},
                       "bar_band": _DARK9, "direction": 1}
SPECS["fig9b_stiff"] = {**_B9, "y": {"side": "right", "labels": [-900, -800, -700, -600, -500, -400, -300, -200, -100, 0]},
                        "bar_band": _LIGHT9, "front_band": _DARK9, "direction": 1,
                        "labels": {"offset": 8, "gap": 12, "width": 150}}
SPECS["fig9c_soft"] = {**_B9, "y": {"side": "left", "labels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}, "bar_band": _DARK9}
SPECS["fig9c_stiff"] = {**_B9, "y": {"side": "right", "labels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
                        "bar_band": _LIGHT9, "front_band": _DARK9}
SPECS["fig9d_soft"] = {**_B9, "y": {"side": "left", "labels": [0, 20, 40, 60, 80, 100, 120]}, "bar_band": _DARK9}

# ---- Fig. 8 (p. 8): Excel charts; grey (ks = 0.1) and black (ks = 1) filled circles on smooth lines.
_L8 = {"labels": {"offset": 45, "gap": 12}, "xlabels": {"offset": 45}, "open_r": 9, "frame_thr": 225}
_X8A = {"labels": [0, 0.5, 1, 1.5, 2, 2.5, 3]}
_Y8A = {"side": "left", "labels": [1, 1.2, 1.4, 1.6, 1.8, 2, 2.2]}
_X8B = {"labels": [0, 0.5, 1, 1.5, 2]}
_Y8B = {"side": "left", "labels": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]}
SPECS["fig8a_soft"] = {"kind": "excel", "mode": "markers", "x": _X8A, "y": _Y8A, "band": (95, 165), "exclude": (0, 70, 2), **_L8}
SPECS["fig8a_stiff"] = {"kind": "excel", "mode": "markers", "x": _X8A, "y": _Y8A, "band": (0, 70), **_L8}
SPECS["fig8b_soft"] = {"kind": "excel", "mode": "markers", "x": _X8B, "y": _Y8B, "band": (95, 165), "exclude": (0, 70, 2), **_L8}
SPECS["fig8b_stiff"] = {"kind": "excel", "mode": "markers", "x": _X8B, "y": _Y8B, "band": (0, 70), **_L8}

# ---- Fig. 7 (p. 7): transverse strain, ks = 1 pN/nm
def _rank7a(k):
    """Fig. 7A: four curves (strain 0 solid black, 0.25 dashed black, 0.5 dash-dot grey, 1 dotted
    light grey), apart for nc of about 15-450, strain 1 on top: read by order."""
    return {"kind": "matlab", "x": _X_NC, "y": _Y_70_110, "band": INK, "close": 3, "mode": "rank", "n": 4,
            "rank": k, "search": 14, "min_half": 2.0, "legend": {"x_from": 150, "ymax": 101}}


for _k, _e in enumerate(["e1", "e05", "e025", "e0"]):
    SPECS[f"fig7a_{_e}"] = _rank7a(_k)

# ---- Fig. S3 (p. 13): two black curves (solid, dashed) that overlap within a line width almost
# everywhere; the solid one is followed, and where the dashed one runs beside it the two merge into
# one run and the interval covers both.
SPECS["figS3_solid"] = {"kind": "matlab", "band": (0, 90), "tick_thr": 170, "tick_len": 6,
                        "x": {"scale": "log10", "ticks": [70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]},
                        "y": {"ticks": [70, 75, 80, 85, 90, 95, 100, 105]},
                        "seeds": [{"x": 150, "rank": -1, "min_half": 2.5, "ymax": 99}], "max_gap": 40, "bend": 0.6}

# ---- Fig. S2 (p. 12): the original model at strains 0, 0.5 and 1; the three marker series lie on
# one curve within a marker's size and are read together (open markers filled by a closing): left
# of the legend each column holds that one curve only, read where it is a single run.
SPECS["figS2l_all"] = {"kind": "matlab", "band": INK, "close": 4, "tick_thr": 150, "x_tick_len": 5,
                       "x": {"scale": "log10", "ticks": [k * 10.0 ** e for e in (-2, -1, 0) for k in range(1, 10)] + [10.0]},
                       "y": {"ticks": [70, 75, 80, 85, 90, 95, 100, 105, 110]},
                       "mode": "rank", "n": 1, "rank": 0, "search": 12, "min_half": 2.0, "trim": 20}
SPECS["figS2r_all"] = {"kind": "matlab", "band": INK, "close": 4, "tick_thr": 150, "x_tick_len": 5,
                       "x": {"scale": "log10", "ticks": LOG_10_1000},
                       "y": {"ticks": [72, 74, 76, 78, 80, 82, 84, 86, 88]},
                       "mode": "rank", "n": 1, "rank": 0, "search": 12, "min_half": 2.0, "trim": 20}

# Fig. 7B is an Excel chart too (light grey frame, labels without ticks on the y axis).
SPECS["fig7b"] = {"kind": "excel", "mode": "markers", "frame_thr": 215,
                  "x": {"labels": [0, 0.25, 0.5, 0.75, 1]},
                  "y": {"side": "left", "labels": [410, 460, 510, 560, 610, 660, 710, 760, 810]},
                  "band": (0, 80), "open_r": 9, "labels": {"offset": 30, "gap": 12}, "xlabels": {"offset": 30}}

