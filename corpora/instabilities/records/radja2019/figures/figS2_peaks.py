# Fig. S2: apex of every peak of the GC chromatogram (linkage analysis) that rises more than
# 150000 above the axis. Calibration from the printed labels 11.00 ... 20.00 (time, min) and
# 1.6e+07 ... 2000000 (abundance), see _chrom.py. The labels "t-Araf" (left end) and "2-Rha",
# "t-Man" (about 12.6-12.95 min) touch the trace on the image: peaks there get no value.
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_chrom", os.path.join(os.path.dirname(__file__), "_chrom.py"))
_chrom = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_chrom)

X_LABELS = [11.0 + i for i in range(10)]
Y_LABELS = [1.6e7, 1.4e7, 1.2e7, 1.0e7, 8.0e6, 6.0e6, 4.0e6, 2.0e6]


def read(image, at):
    return _chrom.read_peaks(image, X_LABELS, Y_LABELS, 25, 150000, exclude=[(10.0, 10.5), (12.6, 12.95)])
