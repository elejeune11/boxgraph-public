# Fig. 2 (p. 2) of jin2015: the critical strain e_c against L_wrinkle/Hf, four blue curves on a
# log-log plot, uniaxial compression. Axes from the panel's own ticks (decade ticks 10, 100 and
# 0.1, 0.01 are the long ones; every minor tick matched to k*10^n). All four curves are the same
# blue, so a curve is picked by its order from the bottom among the blue lines crossing a column
# where all four are apart (`seed_x`), followed column by column from there, and read at `at`
# where it is apart from the others (a local straight-line fit to the run nearest the path).
import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location("jin_helpers", pathlib.Path(__file__).resolve().parent / "_jin.py")
J = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(J)


def calibrate(image):
    box, half = J.frame(image)
    xt = J.merge_ticks(J.ticks(image, box, half, "bottom"), J.ticks(image, box, half, "top"))
    yt = J.merge_ticks(J.ticks(image, box, half, "left"), J.ticks(image, box, half, "right"))
    return box, half, J.log_axis(xt, [10.0, 100.0], 0, 3), J.log_axis(yt, [0.1, 0.01], -3, 0)


def read(image, at, seed_x, order):
    box, half, xax, yax = calibrate(image)
    c0, r0, c1, r1 = box
    m = J.hue_mask(image, "blue")
    margin = int(half) + 34  # frame line and the longest tick
    col = xax.to_pix(seed_x)
    runs = sorted(J.curve_rows(m, col, r0 + margin, r1 - margin), key=lambda t: -t[0])  # bottom first
    if len(runs) <= order:
        return [{"x": x, "y": None, "note": f"only {len(runs)} blue lines at the seed column"} for x in at]
    path = J.follow(m, col, runs[order][0], c0 + margin, c1 - margin, r0 + margin, r1 - margin, max_jump=10)
    tag = (f"blue line {order} from the bottom at L/Hf = {seed_x:g}, followed; x axis from {xax.n} ticks "
           f"(misfit {xax.misfit_px:.1f} px), y axis from {yax.n} ticks (misfit {yax.misfit_px:.1f} px);")
    # steep parts of these thick lines give noisier run centres: accept a local fit residual up to
    # 12 px (it is added to the interval)
    return J.read_curve(m, xax, yax, box, half, at, win=30, margin=margin, tag=tag,
                        guess=lambda c: path.get(int(round(c))), max_res=12.0)
