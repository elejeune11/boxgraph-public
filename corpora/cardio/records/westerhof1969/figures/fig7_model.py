"""Fig. 7: the final model (thick line) at the harmonic frequencies printed in Fig. 4.

The model's points are the vertices of the thick polyline; at each vertex its marker overlaps the
Luchsinger dots and bars, so the vertex is read from the clean line on either side."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig7 as F  # noqa: E402
import _w69 as W  # noqa: E402


def read(image, at):
    cal = F.calibrate(image)
    return W.bold_vertices(cal, "v", at, F.BOLD_HALF, 19, 2.5)
