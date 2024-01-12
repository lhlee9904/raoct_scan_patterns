import numpy as np
import json
from matplotlib import pyplot as plt
from math import pi

from vortex.scan import FreeformScanConfig, FreeformScan, SequentialPattern, XYWaypoints 
from vortex_tools.scan import plot_annotated_waveforms_space

fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, constrained_layout=True, subplot_kw=dict(adjustable='box', aspect='equal'))
cfgs = []
names = []


(r, theta) = np.meshgrid(
    [2, 3, 4],
    np.linspace(0, 2*pi, 200),
    indexing='ij'
)

x = (r + 0.1*np.sin(r + 20*theta)) * np.sin(theta)
y = (r + 0.1*np.sin(r + 20*theta)) * np.cos(theta)

waypoints = np.stack((x, y), axis=-1)
pattern = SequentialPattern().to_pattern(waypoints)

object = XYWaypoints()
cfg = FreeformScanConfig()
cfg.pattern = pattern
for limit in cfg.limits:
    limit.velocity *= 5
    limit.acceleration *= 10
cfg.bypass_limits_check = True
cfg.loop = True

#Original data points
scan = FreeformScan()
scan.initialize(cfg)
data = scan.scan_buffer()
_, ax = plot_annotated_waveforms_space(scan.scan_buffer(), scan.scan_markers(), inactive_marker=None, scan_line='w-')
ax.set_title('Freeform Scan')

#Write the data points of the scan pattern into a txt file
d = open('freeformData.txt', 'w')
print(*data, file = d)

#convert raw data to escaped sequences
raw_data = (data / 10 * 32768 + 32768).astype('uint16').tobytes()
print("printing raw_data")
print(raw_data)

#Write the escaped sequences into a separate txt file
f = open('freeform.txt', 'w')
escaped_string = ''.join([rf'\x{val:02x}' for val in raw_data])
string_for_printing = json.dumps(escaped_string)
print(f'int buffer_length = {len(data)};', file = f)
print(f'const char* buffer = {escaped_string};', file = f)

plt.show()
