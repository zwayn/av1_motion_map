"""
 main.py

  Created by Julien Zouein on 10/11/2023.
  Copyright © 2023 Sigmedia.tv. All rights reserved.
  Copyright © 2023 Julien Zouein (zoueinj@tcd.ie)
----------------------------------------------------------------------------

Main python file calling all the functions.
"""

import os

import cv2
import numpy as np
from tqdm import tqdm

from src.json_processing import get_frame_data
from src.json_processing import get_frame_motion_vectors
from src.json_processing import read_json_file
from src.modules.frame_type import reference_mapping
from src.third_party import flowpy


def main(gop, file, video, width, height):

    os.makedirs(f"output/results/{file}", exist_ok=True)
    os.makedirs(f"output/results/{file}/pngs", exist_ok=True)
    os.makedirs(f"output/results/{file}/pngs/projection", exist_ok=True)
    os.makedirs(f"output/results/{file}/pngs/reference", exist_ok=True)
    os.makedirs(f"output/results/{file}/pngs/mv", exist_ok=True)
    os.makedirs(f"output/results/{file}/npy", exist_ok=True)
    os.makedirs(f"output/results/{file}/stack", exist_ok=True)

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        print("Error opening video stream or file")

    json_file = read_json_file(f"output/json/{file}.json")

    total_frames = len(json_file)

    reference_dict, golden_frames = reference_mapping(0, gop, 0, [])

    for cursor in tqdm(range(1, total_frames-1)):

        ret, frame = cap.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        reference_dict, golden_frames = reference_mapping(cursor, int(gop), 0, golden_frames)

        frame_data = get_frame_data(json_file, cursor)
        motion_field, motion_field_projection, reference_map = get_frame_motion_vectors(
            frame_data,
            reference_dict,
            cursor
        )

        motion_field = motion_field[0:height, 0:width]
        motion_field_projection = motion_field_projection[0:height, 0:width]
        reference_map = reference_map[0:height, 0:width]

        mv_rgb = flowpy.flow_to_rgb(motion_field)
        proj_rgb = flowpy.flow_to_rgb(motion_field_projection)

        stack = np.zeros((height, width, 3), dtype=np.float32)

        stack[:, :, 0] = frame[:, :, 0]/255.
        stack[:, :, 1] = motion_field[:, :, 0]
        stack[:, :, 2] = motion_field[:, :, 1]

        cv2.imshow("stack", proj_rgb)
        cv2.waitKey(10)

        cv2.imwrite(f"output/results/{file}/pngs/projection/{cursor}_motion_projection.png", proj_rgb)
        cv2.imwrite(f"output/results/{file}/pngs/reference/{cursor}_reference_map.png", reference_map)
        cv2.imwrite(f"output/results/{file}/pngs/mv/{cursor}_motion_field.png", mv_rgb)
        np.save(f"output/results/{file}/npy/{cursor}_motion_field.npy", motion_field)
        np.save(f"output/results/{file}/stack/{cursor}_reference_map.npy", stack)

    cv2.destroyAllWindows()
