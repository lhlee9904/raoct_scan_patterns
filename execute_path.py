import os
os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'

from typing import Optional
from pathlib import Path
from tempfile import mkstemp

import nidaqmx
from nidaqmx.constants import AcquisitionType

import numpy as np

from vortex import Range, get_console_logger as get_logger
from vortex.acquire import NullAcquisition
from vortex.process import NullProcessor
from vortex.io import DAQmxIO, DAQmxConfig, AnalogVoltageOutput, AnalogVoltageInput
from vortex.scan import FreeformScanConfig, FreeformScan, Limits, SequentialPattern
from vortex.engine import EngineConfig, Engine, Block, StreamDumpStorage
from vortex.format import FormatPlanner
from vortex.storage import StreamDumpConfig, StreamDump

DOF = 2
VELOCITY_LIMIT = 80e3
ACCELERATION_LIMIT = 25e6
SAMPLES_PER_SECOND = 200_000

RECORDS_PER_BLOCK = 500
PRELOAD_COUNT = 64

LOG_LEVEL = 1

OUTPUT_SCALES = [15, 15]
INPUT_SCALES = [24.02, 24.78]

def run(waypointss: list[np.ndarray], output_path: Optional[Path]=None, prefix: Optional[str]=None, repetitions: int=1):
    if output_path is None:
        output_path = Path()
    if prefix is None:
        prefix = 'data'

    #
    # scan
    #

    cfg = FreeformScanConfig()
    cfg.samples_per_second = SAMPLES_PER_SECOND

    lim = Limits(
        position=Range.symmetric(100),
        velocity=VELOCITY_LIMIT,
        acceleration=ACCELERATION_LIMIT
    )
    cfg.limits = [lim]*DOF

    cfg.loop = False

    # for the full trajectory
    scans = []
    for waypoints in waypointss:
        cfg.pattern = SequentialPattern().to_pattern([waypoints])
        scan = FreeformScan()
        scan.initialize(cfg)
        scans.append(scan)

    print('duration of scans (s)', len(scan.scan_buffer()) / SAMPLES_PER_SECOND)

    #
    # acquisition
    #

    acquire = NullAcquisition()
    ac = acquire.config

    ac.records_per_block = RECORDS_PER_BLOCK
    ac.samples_per_record = 100
    ac.channels_per_sample = 1

    acquire.initialize(ac)

    #
    # processing
    #

    process = NullProcessor()
    pc = process.config

    pc.samples_per_record = acquire.config.samples_per_record
    pc.ascans_per_block = acquire.config.records_per_block

    process.initialize(pc)

    #
    # formatting
    #

    format = FormatPlanner()

    #
    # galvo control
    #

    ioc_out = DAQmxConfig()
    ioc_out.samples_per_block = RECORDS_PER_BLOCK
    ioc_out.samples_per_second = SAMPLES_PER_SECOND
    ioc_out.blocks_to_buffer = PRELOAD_COUNT
    ioc_out.clock.source = 'pfi12'

    ioc_out.name = 'output'

    for (i, scale) in enumerate(OUTPUT_SCALES):
        ioc_out.channels.append(AnalogVoltageOutput(f'Dev1/ao{i}', scale / 10, Block.StreamIndex.GalvoTarget, i))

    io_out = DAQmxIO(get_logger(ioc_out.name, LOG_LEVEL))
    io_out.initialize(ioc_out)

    #
    # input control
    #

    ioc_in = DAQmxConfig()
    ioc_in.samples_per_block = ioc_out.samples_per_block
    ioc_in.samples_per_second = ioc_out.samples_per_second
    ioc_in.blocks_to_buffer = ioc_out.blocks_to_buffer
    ioc_in.clock.source = ioc_out.clock.source
    ioc_in.name = 'input'

    for (i, scale) in enumerate(INPUT_SCALES):
        ioc_in.channels.append(AnalogVoltageInput(f'Dev1/ai{i}', scale / 10, Block.StreamIndex.GalvoActual, i))

    io_in = DAQmxIO(get_logger(ioc_in.name, LOG_LEVEL))
    io_in.initialize(ioc_in)

    #
    # save to disk
    #

    streams = [Block.StreamIndex.GalvoTarget, Block.StreamIndex.GalvoActual]
    endpoints = []
    storages = []
    temps = []

    for stream in streams:
        temps.append(mkstemp())
        sdc = StreamDumpConfig()

        sdc.path = temps[-1][1]
        sdc.stream = stream

        sd = StreamDump()
        sd.open(sdc)
        endpoints.append(StreamDumpStorage(sd))
        storages.append(sd)

    #
    # engine setup
    #

    ec = EngineConfig()
    ec.add_acquisition(acquire, [process])
    ec.add_processor(process, [format])
    ec.add_formatter(format, endpoints)
    ec.add_io(io_out)
    ec.add_io(io_in, preload=False)

    ec.preload_count = PRELOAD_COUNT
    ec.records_per_block = RECORDS_PER_BLOCK
    ec.blocks_to_allocate = 2 * PRELOAD_COUNT
    ec.blocks_to_acquire = 0

    ec.galvo_output_channels = len(io_out.config.channels)
    ec.galvo_input_channels = len(io_in.config.channels)

    engine = Engine(get_logger('engine', LOG_LEVEL))

    engine.initialize(ec)
    engine.prepare()

    #
    # run engine
    #

    # ref: https://stackoverflow.com/questions/53137995/ni-daq-m-series-counter-with-trigger
    clock = nidaqmx.Task()
    pulse = clock.co_channels.add_co_pulse_chan_freq('Dev1/ctr0', freq=SAMPLES_PER_SECOND)
    clock.timing.cfg_implicit_timing(AcquisitionType.CONTINUOUS)

    def engine_event_handler(event, error):
        if event == Engine.Event.Start:
            # start the clock only after the engine has started all hardware
            clock.start()
    engine.event_callback = engine_event_handler

    for _ in range(repetitions):
        for scan in scans:
            engine.scan_queue.append(scan)

    engine.start()
    
    try:
        while not engine.wait_for(0.01):
            pass
    except KeyboardInterrupt:
        print('interrupted')

    engine.stop()

    # finish saving all the data
    for storage in storages:
        storage.close()

    datas = []

    # convert format
    for (stream, (fd, path)) in zip(streams, temps):
        data = np.fromfile(path, dtype=np.float64).reshape((-1, ec.galvo_output_channels))
        datas.append(data)
        np.save(output_path / f'{prefix}-{stream.name}.npy', data)

        # clean up
        os.close(fd)
        os.remove(path)

    return datas

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('path', nargs='+', help='path files to load')
    parser.add_argument('--prefix', type=str, default=None, help='filename prefix for results')
    parser.add_argument('--out', type=str, default=None, help='output directory for results')
    parser.add_argument('--repetitions', type=int, default=1, help='number of times to repeat paths')
    parser.add_argument('--plot', action='store_true', help='immediately plot results')

    args = parser.parse_args()

    prefix = args.prefix
    if prefix is None:
        prefix = Path(args.path[0]).stem

    # load waypoints
    waypoints = [np.load(p) for p in args.path]
    (target, actual) = run(waypoints, args.out, prefix, args.repetitions)

    if args.plot:
        t = np.arange(len(target)) / SAMPLES_PER_SECOND
        names = 'XY'

        from matplotlib import pyplot as plt

        (fig, ax) = plt.subplots()
        for (i, col) in enumerate(actual.T):
            ax.plot(t, col, label=f'actual {names[i]}')
        for (i, col) in enumerate(target.T):
            ax.plot(t, col, label=f'target {names[i]}')
        ax.set_ylabel('position (deg)')
        ax.set_xlabel('time (s)')
        ax.legend()

        (fig, ax) = plt.subplots()
        ax.plot(*actual.T, label=f'actual')
        ax.plot(*target.T, f'--', label=f'target')
        ax.set_xlabel('x (deg)')
        ax.set_ylabel('y (deg)')
        ax.set_aspect(1)
        ax.legend()

        plt.show()
