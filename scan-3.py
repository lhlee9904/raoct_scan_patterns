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
plot_annotated_waveforms_space(scan.scan_buffer(), scan.scan_markers(), inactive_marker=None, scan_line='w-')

raw_data = (data / 10 * 32768 + 32768).astype('uint16').tostring()
print(raw_data)

# #Open file in write mode 
# f = open('file3.txt', 'w')
# print("checkpoint1")
# print('Data for scan-3.py.', file=f)
# print("checkpoint2")
# print((data / 10 * 32768 + 32768).astype('uint16').tobytes(), file = f)
# print("checkpoint3")

plt.show()
# breakpoint()

# print(data)

#data.astype(numpy)
#data.astype('unint16)
#(data / 10 *32768 + 32768).astype('uint16')
# #data
#data.tostring()

#python C:\Users\hyunseo\Downloads\scan_patterns\scan-3.py