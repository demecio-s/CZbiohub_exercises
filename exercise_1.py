# Exercise 1: Write a python script to acquire a multidimensional dataset with 12 z slices
#             spaced by 0.1 um, two channels: DAPI and FITC, and 9 positions distributed in
#             a 3x3 grid with 500 um spacing.

import tifffile  # lets me write as tiff
from pymmcore_plus import CMMCorePlus  # allows to access micromanager
from useq import MDASequence  # useq allows me to run multidimensional sequence

# Defining the attributes for this acquisition
ch = ["DAPI", "FITC"]  # channels
gridPlan = {"rows": 3, "columns": 3, "overlap": 0,
            "fov_width": 1500, 
            "fov_height": 1500
            }  # 3x3 grid with hopefully 500um space between spaces
zSlices = {"range": 1.1, "step": 0.1}  # 12 z-slices with 0.1um step size
metaData = {"channels": ch,
            "z-slice step": zSlices["step"],
            "fov": [gridPlan["fov_width"], gridPlan["fov_width"]],
            "grid": [gridPlan["rows"], gridPlan["columns"]]
            }

# create an instance of micromanager core with the demo config
mmc = CMMCorePlus.instance()
mmc.loadSystemConfiguration(
    r"C:\Program Files\Micro-Manager-2.0\MMConfig_demo.cfg"
    )

# define and run multidimensional acquisition
seq = MDASequence(z_plan=zSlices, channels=ch, grid_plan=gridPlan, metadata=metaData)
run = mmc.run_mda(seq, output=r"exercise_1_data.tif")
