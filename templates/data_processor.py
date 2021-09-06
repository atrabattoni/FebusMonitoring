import logging
import pathlib
import shutil
import warnings

import daspy.io


def data_processor(fname):
    warnings.filterwarnings("ignore")
    drive = pathlib.Path("/run/media/febus/Elements")
    try:
        xarr = daspy.io.read(fname)
        xarr = daspy.io.trim(xarr)
        xarr.to_netcdf(drive / fname.with_suffix(".nc"))
        shutil.move(fname.with_suffix(".log"), drive / fname.with_suffix(".log"))
        fname.unlink()
    except OSError as error:
        logging.info(error)
