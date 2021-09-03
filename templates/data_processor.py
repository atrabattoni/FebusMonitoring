import warnings
import pathlib
import daspy.io
import shutil


def data_processor(fname):
    warnings.filterwarnings("ignore")
    drive = pathlib.Path("/run/media/febus/Elements")
    xarr = daspy.io.read(fname)
    xarr = daspy.io.trim(xarr)
    xarr.to_netcdf(drive / fname.with_suffix(".nc"))
    shutil.move(fname.with_suffix(".log"), drive / fname.with_suffix(".log"))
    fname.unlink()
