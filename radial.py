from math import pi, cos, sin

import numpy as np
import json
from matplotlib import pyplot as plt

from vortex import Range
from vortex.scan import RadialScan, RadialScanConfig
from vortex_tools.scan import plot_annotated_waveforms_space

fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, constrained_layout=True, subplot_kw=dict(adjustable='box', aspect='equal'))
cfgs = []
names = []

cfg = RadialScanConfig()
cfg.segment_extent = Range.symmetric(1)
cfg.segments_per_volume = 10
cfg.samples_per_segment = 50
for limit in cfg.limits:
    limit.acceleration *= 5
cfg.loop = True

#Original data points
scan = RadialScan()
scan.initialize(cfg)
data = scan.scan_buffer()
plot_annotated_waveforms_space(scan.scan_buffer(), scan.scan_markers(), inactive_marker=None, scan_line='w-')

#Write the data points of the scan pattern into a txt file
d = open('radialData.txt', 'w')
print(*data, file = d)

#convert raw data to escaped sequences
raw_data = (data / 10 * 32768 + 32768).astype('uint16').tobytes()
print("printing raw_data")
print(raw_data)

#Write the escaped sequences into a separate txt file
f = open('radial.txt', 'w')
escaped_string = ''.join([rf'\x{val:02x}' for val in raw_data])
string_for_printing = json.dumps(escaped_string)
print(f'int buffer_length = {len(data)};', file = f)
print(f'const char* buffer = {escaped_string};', file = f)

# change offset
names.append('Offset')
cfgs.append(cfg.copy())
cfgs[-1].offset = (1, 0)

# change extent
names.append('Extent')
cfgs.append(cfg.copy())
cfgs[-1].volume_extent = Range(0, 5)
cfgs[-1].segment_extent = Range(0.5, 1)

# change shape
names.append('Shape')
cfgs.append(cfg.copy())
cfgs[-1].segments_per_volume = 5

# change rotation
names.append('Angle')
cfgs.append(cfg.copy())
cfgs[-1].angle = pi / 6

for (name, cfg, ax) in zip(names, cfgs, axs.flat):
    scan = RadialScan()
    scan.initialize(cfg)
    plot_annotated_waveforms_space(scan.scan_buffer(), scan.scan_markers(), inactive_marker=None, scan_line='w-', axes=ax)
    ax.set_title(name)

    if not np.allclose(cfg.offset, (0, 0)):
        ax.plot([0, cfg.offset[0]], [0, cfg.offset[1]], 'ro-', zorder=20)
    if cfg.angle != 0:
        ax.plot([1, 0, cos(cfg.angle)], [0, 0, sin(cfg.angle)], 'ro-', zorder=20)

x = np.abs(axs.flat[0].get_xlim()).max()
axs.flat[0].set_xlim(-x, x)

plt.show()