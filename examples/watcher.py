from febus import FebusDevice, Watcher
import warnings
import pathlib
import daspy
import shutil


def data_processor(fname):
    warnings.filterwarnings("ignore")
    drive = pathlib.Path("/run/media/febus/Elements")
    xarr = daspy.io.read(fname)
    xarr = daspy.io.trim(xarr)
    xarr.to_netcdf(drive / fname.with_suffix(".nc"))
    shutil.move(fname.with_suffix(".log"), drive / fname.with_suffix(".log"))
    fname.unlink()
    print(fname)


device = FebusDevice()
device.start_server(gps=False)
device.start_acquisition(40000, 1, 2, 30, 500, 1, 40,
                         "/home/febus/Pipelines/SR_writer.py")
device.enable_writings()
watcher = Watcher(device, data_processor=data_processor)
watcher.start_monitoring()
