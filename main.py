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
from src.json_processing import get_frame_reference
from src.json_processing import read_json_file
from src.third_party import flowpy

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
parser.add(
    "--height",
    required=True,
    type=int,
    help="height of the input video.",
)
parser.add(
    "--width",
    required=True,
    type=int,
    help="width of the input video.",
)
parser.add(
    "--fps",
    required=True,
    type=int,
    help="fps of the input video.",
)
parser.add(
    "--video",
    required=True,
    type=str,
    help="path to the input video.",
)

arg_flags = parser.parse_args()

version = "0.1.0"

if __name__ == "__main__":

    if arg_flags.version:

        print(version)
        exit()

    os.makedirs(f"output/results/{arg_flags.input}", exist_ok=True)
    os.makedirs(f"output/results/{arg_flags.input}/pngs", exist_ok=True)
    os.makedirs(f"output/results/{arg_flags.input}/pngs/intensity", exist_ok=True)
    os.makedirs(f"output/results/{arg_flags.input}/pngs/reference", exist_ok=True)
    os.makedirs(f"output/results/{arg_flags.input}/pngs/mv", exist_ok=True)
    os.makedirs(f"output/results/{arg_flags.input}/npy", exist_ok=True)
    os.makedirs(f"output/results/{arg_flags.input}/stack", exist_ok=True)

    cap = cv2.VideoCapture(arg_flags.video)
    if not cap.isOpened():
        print("Error opening video stream or file")

    results = []

    json_file = read_json_file(f"output/json/{arg_flags.input}.json")

    total_frames = len(json_file)

    w = len(json_file[0]['motionVectors'][0])*4
    h = len(json_file[0]['motionVectors'])*4

    for cursor in tqdm(range(1, total_frames-1)):

        ret, frame = cap.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

        frame_data = get_frame_data(json_file, cursor)
        motion_field, motion_intensity = get_frame_motion_vectors(frame_data)
        reference_map = get_frame_reference(frame_data)

        motion_field = motion_field[0:arg_flags.height, 0:arg_flags.width]
        motion_intensity = motion_intensity[0:arg_flags.height, 0:arg_flags.width]
        reference_map = reference_map[0:arg_flags.height, 0:arg_flags.width]

        mv_rgb = flowpy.flow_to_rgb(motion_field)

        stack = np.zeros((arg_flags.height, arg_flags.width, 3), dtype=np.float32)

        stack[:, :, 0] = frame[:, :, 0]/255.
        stack[:, :, 1] = motion_field[:, :, 0]
        stack[:, :, 2] = motion_field[:, :, 1]

        cv2.imshow("stack", cv2.cvtColor(stack, cv2.COLOR_YCrCb2BGR))
        cv2.waitKey(10)

        cv2.imwrite(f"output/results/{arg_flags.input}/pngs/intensity/{cursor}_motion_intensity.png", motion_intensity)
        cv2.imwrite(f"output/results/{arg_flags.input}/pngs/reference/{cursor}_reference_map.png", reference_map)
        cv2.imwrite(f"output/results/{arg_flags.input}/pngs/mv/{cursor}_motion_field.png", mv_rgb)
        np.save(f"output/results/{arg_flags.input}/npy/{cursor}_motion_field.npy", motion_field)
        np.save(f"output/results/{arg_flags.input}/stack/{cursor}_reference_map.npy", stack)

    cv2.destroyAllWindows()
