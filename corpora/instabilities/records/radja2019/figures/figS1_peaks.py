# Fig. S1: apex of every peak of the GC chromatogram (composition analysis) that rises more than
# 100000 above the axis. Calibration from the printed labels 14.00 ... 36.00 (time, min) and
# 6500000 ... 500000 (abundance), see _chrom.py. The "Ara" labels at the left end touch the
# trace on the image, so nothing is read before 14.6 min. The large Glc peak near 27.4 min runs
# off the top of the plot and gets no value.
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_chrom", os.path.join(os.path.dirname(__file__), "_chrom.py"))
_chrom = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_chrom)

X_LABELS = [14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0]
Y_LABELS = [6500000 - 500000 * i for i in range(13)]


def read(image, at):
    return _chrom.read_peaks(image, X_LABELS, Y_LABELS, 25, 100000, exclude=[(13.5, 14.6)])
