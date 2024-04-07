
# In a new python script, set up a timelapse acquisition with 100 time points in the DAPI channel with exposure time of 10 ms. 
# Extend your acquisition pipeline to inspect each image as it is acquired. If a pixel has a value of exactly 700 counts, set 
# neighboring pixels within a radius of 15 pixels to zero. Save this modified image in the .tif dataset instead of the original image.

import tifffile
import numpy as np
from pymmcore_plus import CMMCorePlus
from useq import MDASequence, MDAEvent

# open instance with demo config as in exercise 1
mmc = CMMCorePlus.instance()
mmc.loadSystemConfiguration(r"C:\Program Files\Micro-Manager-2.0\MMConfig_demo.cfg")
mmc.setProperty("Camera", "Mode", "Noise")  # changes camera mode to noise

# defining attributes for this acquisition
ch = [{"config": "DAPI", "exposure": 10}]  # 10 ms exposure
timePlan = {"interval": 0, "loops": 100}  # 100 time points
metaData = {"channels": ch[0]["config"],
            "time points": timePlan["loops"]
            }

# pixel value target and radius to set to zero
target = 700
radius = 15

# def multi-dimensional acquisition
seq = MDASequence(channels=ch, time_plan=timePlan, metadata=metaData)

# checks if pixel at (x, y) is located within radius centered at coords and sets to 0
def check_radius(data: np.ndarray, coords: list):
    if len(coords) == 0:
        return data
    for coord in coords:
        for x in range(len(data)):
            for y in range(len(data[0])):
                rad_sq = (x-coord[0])**2 + (y-coord[1])**2  # circle centered at coords
                if rad_sq <= (radius**2):
                    data[x, y] = 0
                else:
                    pass
    return data

# edits every image captured during acquisition process. Modified from 
# on_image_captured function at: https://pymmcore-plus.github.io/pymmcore-plus/guides/events/
@mmc.mda.events.frameReady.connect
def on_image_captured(data: np.ndarray, event: MDAEvent): 
    coords_spec = []  # all coords which have pixel valuye of 700 go here
    print(f"Event index {event.index} captured with shape {data.shape}")

    # first check for all pixels with value = 700 and save coordinates
    for x in range(len(data)):
        for y in range(len(data[0])):
            if data[x ,y] == target:
                data[x ,y] = 0
                coords_spec.append([x ,y])
    # then begin checking for all pixels within radius of 15 centered at coords_spec
    data = check_radius(data, coords_spec)
    if len(coords_spec) != 0:
        print("700 pixel value at:", coords_spec)


run = mmc.run_mda(seq, output=r"exercise_2_data.tif")
