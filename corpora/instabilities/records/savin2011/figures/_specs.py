"""Panel specifications for the readings of savin2011, read by _common.py.

Each entry gives, for one reading: the printed tick labels matched to the detected ticks (in order
from the axis origin), the series colour as seen in the image (sampled from the rendered crop), the
size of the square used to strip thin lines from the markers (`open`, px), and regions excluded
(panel letters, legends, insets; pixels in the crop). Nothing here is a value read from the paper
except the tick labels.
"""

STAGES = [8, 12, 16]  # E8, E12, E16 as embryonic days

_S8 = {"x": {"labels": STAGES}, "bars": True, "band": 4, "gap": 8, "snap": STAGES, "one_per_x": True,
       "expect": 3, "exclude": [[1700, 1550, 1900, 1760]]}
_S8_OBS = {"color": "#000000", "tol": 90, "open": 41, "min_area": 1500}
_S8_SIM = {"color": "#b848e8", "tol": 45, "open": 21, "min_area": 400}
_S8_EQ3 = {"color": "#7808a8", "tol": 45, "hollow": True, "open": 21, "min_area": 400}
_S8B_Y = {"y": {"labels": [0, 4, 8], "origin_at_axis": True}}
_S8C_Y = {"y": {"labels": [0, 1, 2], "origin_at_axis": True}}

SPECS = {
    # Fig. S8b,c (p. 17): lambda and R of the chick gut; squares measured, filled circles simulation,
    # open circles Eq. 3 / Eq. 4. Error bars s.d.
    "figS8b_obs": {**_S8, **_S8B_Y, **_S8_OBS},
    "figS8b_sim": {**_S8, **_S8B_Y, **_S8_SIM},
    "figS8b_eq3": {**_S8, **_S8B_Y, **_S8_EQ3},
    "figS8c_obs": {**_S8, **_S8C_Y, **_S8_OBS},
    "figS8c_sim": {**_S8, **_S8C_Y, **_S8_SIM},
    "figS8c_eq4": {**_S8, **_S8C_Y, **_S8_EQ3},
}

DAYS = list(range(8, 17))  # E8 ... E16, one tick per day
_F3_STAGE = {"x": {"labels": [7] + DAYS, "origin_at_axis": True, "major_frac": 0}, "snap": DAYS, "one_per_x": True, "bars": True, "band": 3, "gap": 8}
SPECS.update({
    # Fig. 3b (p. 3): ro (dark) and ri (light) against stage; the micrograph inset above the frame is cut.
    "fig3b_ro": {**_F3_STAGE, "y": {"labels": [0.0, 0.1, 0.2, 0.3, 0.4], "origin_at_axis": True, "major_frac": 0},
                 "color": "#282878", "tol": 28, "open": 31, "min_area": 500, "exclude": [[0, 0, 2940, 130]]},
    "fig3b_ri": {**_F3_STAGE, "y": {"labels": [0.0, 0.1, 0.2, 0.3, 0.4], "origin_at_axis": True, "major_frac": 0},
                 "color": "#4848a8", "tol": 28, "open": 31, "min_area": 500, "exclude": [[0, 0, 2940, 130]]},
    # Fig. 3c (p. 3): Lt (blue) and Lm (red) against stage; inset photograph excluded.
    "fig3c_Lt": {**_F3_STAGE, "y": {"labels": [0, 50, 100, 150, 200], "origin_at_axis": True, "major_frac": 0},
                 "color": "#3848a8", "tol": 45, "open": 31, "min_area": 500, "exclude": [[560, 80, 2310, 850]]},
    "fig3c_Lm": {**_F3_STAGE, "y": {"labels": [0, 50, 100, 150, 200], "origin_at_axis": True, "major_frac": 0},
                 "color": "#e82828", "tol": 45, "open": 31, "min_area": 500, "exclude": [[560, 80, 2310, 850]]},
})
# the same points at E8, E12 and E16 only, the stages of Table 1, for point-by-point comparison
for _k in ("fig3b_ro", "fig3b_ri", "fig3c_Lt"):
    SPECS[_k + "_t1"] = {**SPECS[_k], "only_x": STAGES}
SPECS.update({
    # Fig. 3f (p. 3): Em (red) and Et (blue), log axis 10^3 ... 10^6 Pa (10^3 on the axis line).
    "fig3f_Em": {**_F3_STAGE, "y": {"labels": [1e3, 1e4, 1e5, 1e6], "scale": "log10", "origin_at_axis": True},
                 "color": "#e82828", "tol": 45, "open": 31, "min_area": 500},
    "fig3f_Et": {**_F3_STAGE, "y": {"labels": [1e3, 1e4, 1e5, 1e6], "scale": "log10", "origin_at_axis": True},
                 "color": "#3848a8", "tol": 45, "open": 31, "min_area": 500},
    # Fig. 3g (p. 3): eps0 (%), black squares.
    "fig3g_e0": {**_F3_STAGE, "y": {"labels": [0, 10, 20, 30, 40], "origin_at_axis": True},
                 "color": "#000000", "tol": 90, "open": 31, "min_area": 500},
})

# Fig. 4b, c (p. 4): log-log, x 10-100 (b) and 1-30 (c); the minor ticks are matched to 20 ... 90 (b) and
# 2 ... 9, 20 (c); the lower-left corner is the first decade (on the axis lines); the mark next to it is the
# black line leaving the corner, not a tick.
_LOG10_100 = {"labels": [10, 20, 30, 40, 50, 60, 70, 80, 90], "scale": "log10", "origin_at_axis": True,
              "major_frac": 0}
_LOG1_20 = {"labels": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20], "scale": "log10", "origin_at_axis": True,
            "major_frac": 0}
_F4B = {"x": _LOG10_100, "y": _LOG10_100, "bars": True, "band": 4, "gap": 8}
_F4C = {"x": _LOG1_20, "y": _LOG1_20, "bars": True, "band": 4, "gap": 8}
_CHICK = {"color": "#000000", "tol": 90, "open": 41, "min_area": 2000, "shape": "square", "expect": 3}
# rubber triangles: stacked in shared columns, so a bar cannot be told from its neighbours' (no bars read);
# where a triangle's plotted point lies within it is not known: +-9 px (a sixth of its height) added
_RUBBER = {"color": "#38b838", "tol": 50, "open": 25, "min_area": 300, "shape": "triangle", "bars": False,
           "extra_px": 9}
SPECS.update({
    "fig4b_chick": {**_F4B, **_CHICK},
    "fig4b_rubber": {**_F4B, **_RUBBER},
    "fig4c_chick": {**_F4C, **_CHICK},
    "fig4c_rubber": {**_F4C, **_RUBBER},
})

# Fig. S3 (p. 10): force against distance, log-log; x ticks 2 ... 9 with 1 on the y axis line; y decades
# 10^-6 ... 10^-3 (the frame's lower edge is not a decade). The inset (and its labels) is excluded.
_S3 = {"x": {"labels": [1, 2, 3, 4, 5, 6, 7, 8, 9], "scale": "log10", "origin_at_axis": True, "major_frac": 0},
       "y": {"labels": [1e-6, 1e-5, 1e-4, 1e-3], "scale": "log10", "major_frac": 0},
       "bars": True, "band": 3, "gap": 8, "open": 41, "min_area": 800, "exclude": [[690, 1700, 2250, 3000]]}
SPECS.update({
    "figS3_rb0398": {**_S3, "color": "#480888", "tol": 45},
    "figS3_rb0253": {**_S3, "color": "#f84808", "tol": 45},
    "figS3_rb0122": {**_S3, "color": "#088808", "tol": 45},
})

# Fig. S6c (p. 14): b1par h/(k2 a1^3) against k1/k2, log-log; every minor tick matched (x 3 ... 200, y 2 ... 90,
# y = 1 on the x axis line). Panel letter excluded.
SPECS["figS6c_pts"] = {
    "x": {"labels": [3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200], "scale": "log10",
          "major_frac": 0},
    "y": {"labels": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90], "scale": "log10",
          "origin_at_axis": True, "major_frac": 0},
    "color": "#000000", "tol": 90, "open": 45, "min_area": 2000, "shape": "square", "bars": True, "band": 4,
    "gap": 8, "exclude": [[150, 60, 350, 250]], "expect": 6}

# Fig. S1 (p. 8): cells per mm^2 in the eight slices a-h of the E12 tube section, red bars with black s.d. bars;
# y ticks 200, 400, 600 and 0 on the axis line (the 800 label stands at the frame's top edge, no tick)
SPECS["figS1_bars"] = {"kind": "bars", "x": {}, "y": {"labels": [0, 200, 400, 600], "origin_at_axis": True},
                       "color": "#ff0000", "tol": 80, "min_area": 5000, "band": 3, "gap": 4, "expect": 8}

# Figs. S9 (quail), S10 (finch), S11 (mouse) (pp. 19, 19, 20): panels a-g as in Fig. 3, the species in colour,
# the chick in grey (not read here: the chick values are read from Fig. 3). Stages fall on half days for the
# mouse, so points snap to a half-day grid. Legends (d, e), the volume inset (c) and the panel letter (g)
# are excluded (crop pixels at 1200 dpi).
HALF_DAYS = [6 + 0.5 * i for i in range(25)]  # E6 ... E18 (the finch lengths start at E7)
# the frame's left edge stands at E7 (one tick spacing before E8, as on every stage axis of the paper): anchoring
# it removes the tie between the true mapping and one shifted by a day
_SX = {"labels": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], "origin_at_axis": True, "major_frac": 0}
_SI_STAGE = {"x": _SX, "snap": HALF_DAYS, "one_per_x": True, "bars": True, "band": 3, "gap": 8, "open": 25,
             "min_area": 300}
_SI_PANELS = {
    "a_h": {"y": {"labels": [0, 10, 20], "origin_at_axis": True}, "color": "#f80808", "tol": 60},
    "b_ro": {"y": {"labels": [0.0, 0.1, 0.2, 0.3, 0.4], "origin_at_axis": True}, "color": "#080888", "tol": 40},
    "b_ri": {"y": {"labels": [0.0, 0.1, 0.2, 0.3, 0.4], "origin_at_axis": True}, "color": "#3838f8", "tol": 40},
    "c_Lt": {"y": {"labels": [0, 50, 100, 150], "origin_at_axis": True}, "color": "#0808f8", "tol": 40,
             "exclude": [[330, 100, 1700, 1080]]},
    "c_Lm": {"y": {"labels": [0, 50, 100, 150], "origin_at_axis": True}, "color": "#f80808", "tol": 60,
             "exclude": [[330, 100, 1700, 1080]]},
    "f_Em": {"y": {"labels": [1e4, 1e5, 1e6], "scale": "log10"}, "color": "#f80808", "tol": 60},
    "f_Et": {"y": {"labels": [1e4, 1e5, 1e6], "scale": "log10"}, "color": "#0808f8", "tol": 40},
    "g_e0": {"y": {"labels": [0, 10, 20, 30, 40, 50, 60], "origin_at_axis": True}, "color": "#000000", "tol": 90,
             "exclude": [[2250, 600, 2550, 1000]], "shape": "square"},
}
# d: x matched on the 100, 150, 200 ticks (0 and 50 lie under the points on the axis; listing them lets a
# mapping shifted by one label tie with the true one)
_SD = {"x": {"labels": [100, 150, 200], "major_frac": 0}, "y": {"labels": [0, 1e5, 2e5], "origin_at_axis": True},
       "bars": True, "band": 3, "gap": 8, "open": 21, "min_area": 200, "exclude": [[1650, 100, 2550, 480]],
       "tick_cap": 50}  # ticks are ~25 px long; the black linearisation lines standing on the axis are longer
_SE = {"x": {"labels": [0, 2, 4, 6, 8], "origin_at_axis": True, "major_frac": 0},
       "y": {"labels": [0, 200, 400, 600], "origin_at_axis": True},
       "bars": True, "band": 3, "gap": 8, "open": 21, "min_area": 200, "exclude": [[1750, 100, 2550, 480]]}
SI_SPECIES = {  # figure, page, (dx, dy) of its crops from S9's, early and late stage
    "S9": ("quail", 19, (0, 0), "E12", "E15"),
    "S10": ("finch", 19, (0, 5712), "E10", "E13"),
    "S11": ("mouse", 20, (90, -60), "E14.5", "E16.5"),
}
_S9_CROPS = {"a": [1000, 1238, 3550, 3278], "b": [3550, 1238, 6150, 3278], "c": [6250, 1238, 8800, 3278],
             "d": [1000, 3288, 3550, 5388], "e": [3550, 3288, 6150, 5388], "f": [6250, 3288, 8800, 4238],
             "g": [6250, 4233, 8800, 5388]}
for _fig, (_sp, _pg, (_dx, _dy), _early, _late) in SI_SPECIES.items():
    for _k, _v in _SI_PANELS.items():
        SPECS[f"fig{_fig}{_k}"] = {**_SI_STAGE, **_v}
    _sd = _SD if _fig != "S11" else {**_SD, "x": {"labels": [150, 200], "major_frac": 0}}  # S11d: 100 hidden
    SPECS[f"fig{_fig}d_{_early}"] = {**_sd, "color": "#f80808", "tol": 60, "shape": "square"}
    SPECS[f"fig{_fig}d_{_late}"] = {**_sd, "color": "#f89898", "tol": 40}
    SPECS[f"fig{_fig}e_{_early}"] = {**_SE, "color": "#0808f8", "tol": 40, "shape": "square"}
    SPECS[f"fig{_fig}e_{_late}"] = {**_SE, "color": "#9898f8", "tol": 40}
    # the stage of Table 2 only (quail E12, finch E13, mouse E16.5), for point-by-point comparison
    _t2 = {"S9": 12, "S10": 13, "S11": 16.5}[_fig]
    for _k in ("a_h", "b_ro", "b_ri", "c_Lt", "f_Em", "f_Et", "g_e0"):
        SPECS[f"fig{_fig}{_k}_t2"] = {**SPECS[f"fig{_fig}{_k}"], "only_x": [_t2]}


def si_crop(fig, panel):
    """The crop of a panel of Fig. S9, S10 or S11 at 1200 dpi."""
    _, _, (dx, dy), _, _ = SI_SPECIES[fig]
    c = _S9_CROPS[panel]
    return [c[0] + dx, c[1] + dy, c[2] + dx, c[3] + dy]


# Fig. 1b (p. 2): raster bar charts of cells per mm^2 (tube blue, mesentery red) at E5 (three regions) and
# E12 (one bar per vasculature region); grey axes without tick marks, so y is calibrated from the label text
# (label_box: the label column, in crop pixels; plot: the bar region, in crop pixels).
SPECS.update({
    "fig1b_E5_tube": {"kind": "bars", "y": {"labels": [200, 400, 600, 800], "label_box": [21, 107, 235, 813]},
                      "plot": [246, 21, 1530, 877], "color": "#3c50b4", "tol": 90, "min_area": 3000,
                      "band": 4, "gap": 4, "expect": 3},
    "fig1b_E12_tube": {"kind": "bars", "y": {"labels": [100, 200, 300, 400], "label_box": [11, 150, 214, 813]},
                       "plot": [225, 11, 1700, 916], "color": "#3c50b4", "tol": 90, "min_area": 1000,
                       "band": 3, "gap": 4},
    "fig1b_E5_mes": {"kind": "bars", "y": {"labels": [200, 400, 600, 800], "label_box": [11, 32, 225, 492]},
                     "plot": [246, 128, 1530, 552], "color": "#e6283a", "tol": 90, "min_area": 3000,
                     "band": 4, "gap": 4, "expect": 3},
    "fig1b_E12_mes": {"kind": "bars", "y": {"labels": [20, 40, 60], "label_box": [32, 21, 182, 492]},
                      "plot": [203, 0, 1680, 616], "color": "#e6283a", "tol": 90, "min_area": 1000,
                      "band": 3, "gap": 4},
})

# Fig. 3d, e (p. 3): stress-strain points of mesentery (d) and tube (e) at E8, E12, E16, with x and y error
# bars (s.d.); stress labels are printed in units of 10^5 Pa (d) and 10^2 Pa (e) and entered here in Pa.
# x: the 0 and 50 ticks are hidden under the points lying on the axis; the labels of the visible ticks, 100,
# 150, 200, are matched (the eps0 bracket and the black line standing on the axis are off the spacing)
_F3D = {"x": {"labels": [100, 150, 200], "major_frac": 0},
        "y": {"labels": [0, 1e5, 2e5], "origin_at_axis": True},
        "bars": True, "band": 3, "gap": 8, "open": 25, "min_area": 300,
        "exclude": [[370, 50, 1520, 940], [1650, 90, 2200, 510], [1470, 1020, 1640, 1160]]}
_F3E = {"x": {"labels": [0, 2, 4, 6, 8], "origin_at_axis": True},
        "y": {"labels": [0, 200, 400, 600], "origin_at_axis": True},
        "bars": True, "band": 3, "gap": 8, "open": 25, "min_area": 300,
        "exclude": [[450, 120, 1600, 1010], [1980, 150, 2480, 590], [1420, 1580, 1540, 1760]]}
SPECS.update({
    "fig3d_E16": {**_F3D, "color": "#f87888", "tol": 30},
    "fig3d_E12": {**_F3D, "color": "#e82828", "tol": 30, "shape": "square"},
    "fig3d_E8": {**_F3D, "color": "#981818", "tol": 30, "shape": "diamond"},
    "fig3e_E16": {**_F3E, "color": "#8888c8", "tol": 30},
    "fig3e_E12": {**_F3E, "color": "#3848a8", "tol": 16, "shape": "square"},
    "fig3e_E8": {**_F3E, "color": "#383888", "tol": 16, "shape": "diamond"},
})
