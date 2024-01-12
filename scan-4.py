from math import pi, cos, sin

import numpy as np
import json
from matplotlib import pyplot as plt

from vortex import Range
from vortex.scan import RasterScan, RasterScanConfig
from vortex_tools.scan import plot_annotated_waveforms_space

fig, axs = plt.subplots(1, 2, sharex=True, sharey=True, constrained_layout=True, subplot_kw=dict(adjustable='box', aspect='equal'))
cfgs = []
names = []

cfg = RasterScanConfig()
cfg.volume_extent = Range.symmetric(1)
cfg.bscan_extent = Range.symmetric(1)
cfg.samples_per_segment = 20
cfg.segments_per_volume = 10
for limit in cfg.limits:
    limit.velocity *= 10
    limit.acceleration *= 40
cfg.loop = True

scan = RasterScan()
scan.initialize(cfg)
data = scan.scan_buffer()
plot_annotated_waveforms_space(scan.scan_buffer(), scan.scan_markers(), inactive_marker=None, scan_line='w-')

print("checkpoint")
raw_data = (data / 10 * 32768 + 32768).astype('uint16').tobytes()
escaped_string = ''.join([rf'\x{val:02x}' for val in raw_data])
string_for_printing = json.dumps(escaped_string)
print("printing data")
print(data)
print(*data) #to print everything 
d = open('data8.txt', 'w')
print(*data, file = d)
print("printing raw_data")
print(raw_data)

# breakpoint()

#Open file in write mode 
f = open('file8.txt', 'w')
print("checkpoint1")
original_string = (data / 10 * 32768 + 32768).astype('uint16').tostring().decode('latin-1')
#string_for_printing = json.dumps(original_string)
#print((data / 10 * 32768 + 32768).astype('uint16').tostring(), file = f)
#print(f'const char* buffer = {raw_data};', file = f)
#originally string_for_printing 
print(f'int buffer_length = {len(data)};', file = f)
print("checkpoint3")
print(len(data))

print("checkpoint4")
print(escaped_string)  #replaces escaped_string
print(f'const char* buffer = {escaped_string};', file = f)
print("checkpoint5")

#Find a way to attatch quotation marks for the buffer 

#___________________________
plt.show()

# cfgs.append(cfg.copy())
# names.append('Raster Scan - Unidirectional')

# cfgs.append(cfg.copy())
# cfgs[-1].bidirectional_segments = True
# names.append('Raster Scan - Bidirectional')

# for (name, cfg, ax) in zip(names, cfgs, axs):
#     scan = RasterScan()
#     scan.initialize(cfg)

#     for segment in cfg.to_waypoints():
#         ax.plot(segment[:, 0], segment[:, 1], 'x')

    # path = scan.scan_buffer()
    # ax.plot(path[:, 0], path[:, 1], 'w-', lw=1, zorder=-1)

    # ax.set_xlabel('x (au)')
    # ax.set_ylabel('y (au)')
    # ax.set_title(name)
