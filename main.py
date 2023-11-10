"""
 main.py

  Created by Julien Zouein on 10/11/2023.
  Copyright © 2023 Sigmedia.tv. All rights reserved.
  Copyright © 2023 Julien Zouein (zoueinj@tcd.ie)
----------------------------------------------------------------------------

Main python file calling all the functions.
"""

import os

import configargparse
import cv2
import numpy as np
from tqdm import tqdm

from src.json_processing import get_frame_data
from src.json_processing import get_frame_motion_vectors
from src.json_processing import read_json_file

parser = configargparse.ArgParser()
parser.add(
    "--config",
    required=False,
    is_config_file=True,
    help="Config file path."
)
parser.add(
    "--version",
    required=False,
    default=False,
    action="store_true",
    help="Display the version of the Software.",
)
parser.add(
    "--input",
    required=True,
    help="name of the input file.",
)

arg_flags = parser.parse_args()

version = "0.1.0"

if __name__ == "__main__":

    if arg_flags.version:

        print(version)
        exit()

    os.makedirs(f"output/results/{arg_flags.input}", exist_ok=True)
    os.makedirs(f"output/results/{arg_flags.input}/pngs", exist_ok=True)
    os.makedirs(f"output/results/{arg_flags.input}/npy", exist_ok=True)

    results = []

    json_file = read_json_file(f"output/json/{arg_flags.input}.json")

    total_frames = len(json_file)

    w = len(json_file[0]['motionVectors'][0])*4
    h = len(json_file[0]['motionVectors'])*4

    for cursor in tqdm(range(1, total_frames-1)):

        frame_data = get_frame_data(json_file, cursor)
        motion_field, motion_intensity = get_frame_motion_vectors(frame_data)

        cv2.imwrite(f"output/results/{arg_flags.input}/pngs/{cursor}_motion_intensity.png", motion_intensity)
        np.save(f"output/results/{arg_flags.input}/npy/{cursor}_motion_field.npy", motion_field)

    cv2.destroyAllWindows()