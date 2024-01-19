from math import pi, cos, sin

import numpy as np
from matplotlib import pyplot as plt

from vortex import Range
from vortex.scan import RasterScan, RasterScanConfig
from vortex_tools.scan import plot_annotated_waveforms_space

fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, constrained_layout=True, subplot_kw=dict(adjustable='box', aspect='equal'))
cfgs = []
names = []

cfg = RasterScanConfig()
cfg.segment_extent = Range.symmetric(1)
cfg.segments_per_volume = 10
cfg.samples_per_segment = 50
for limit in cfg.limits:
    limit.acceleration *= 5
cfg.loop = True

scan = RasterScan()
scan.initialize(cfg)
data = scan.scan_buffer()
print(*data)
np.save('scan_pattern.npy', data)