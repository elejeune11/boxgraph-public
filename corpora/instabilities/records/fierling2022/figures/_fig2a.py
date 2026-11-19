"""Shared calibration for the strain-profile panels Fig. 2a (PDF p. 5) and Supp. Fig. 1e (PDF p. 23)
(gnuplot, see _gp.py and _fig2.py).

x: as in _fig2.py (frame lines 0 and pi/2, long inward ticks pi/8 and pi/4).
y: given by each panel as (printed label, where): frame lines, the major inward ticks on the left
frame line from the top, and the long black 'Original size' line at 1 (its tick lies under it).
A step line lying on the bottom frame line is read from its upper edge (see _gp.read_lines).
"""
import _fig2
import _gp

STEELBLUE, DBLUE, DCYAN = (48, 96, 128), (0, 0, 139), (0, 238, 238)


def read_line(image, at, ylabels, rgb, rows, tol=50, win=12):
    spec = {"ylabels": ylabels, "xlabels": _fig2.XLABELS, "rgb": rgb, "tol": tol, "win": win, "rows": rows}
    return _gp.read_lines(image, at, spec)
