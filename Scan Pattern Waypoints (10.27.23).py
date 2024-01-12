from vortex import Range
from vortex.scan import RasterScan
from vortex_tools.scan import plot_annotated_waveforms_space

scan = RasterScan()
cfg = scan.config
cfg.volume_extent = Range.symmetric(2)
cfg.samples_per_segment = 100
for limit in cfg.limits:
    limit.acceleration *= 5
cfg.loop = True
scan.initialize(cfg)

_, ax = plot_annotated_waveforms_space(scan.scan_buffer(), scan.scan_markers(), inactive_marker=None, scan_line='w-')
ax.set_title('Raster')