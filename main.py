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
from src.modules.utils import update_stack
from src.third_party import flowpy


def main(gop, file, video, width, height, forward, dataset, layers, step, encoding_preset, display):

    os.makedirs(f"output/results/{file}", exist_ok=True)
    os.makedirs(f"output/results/{file}/pngs", exist_ok=True)
    os.makedirs(f"output/results/{file}/pngs/projection", exist_ok=True)
    os.makedirs(f"output/results/{file}/pngs/reference", exist_ok=True)
    os.makedirs(f"output/results/{file}/pngs/mv", exist_ok=True)
    os.makedirs(f"output/results/{file}/npy", exist_ok=True)
    os.makedirs(f"output/results/{file}/npy/mv", exist_ok=True)
    os.makedirs(f"output/results/{file}/npy/mv_proj", exist_ok=True)
    os.makedirs(f"output/results/{file}/stack", exist_ok=True)

    if dataset:
        name = f"{encoding_preset}_{step}_{gop}"
        for layer in layers:
            name += f"_{layer}"
        os.makedirs(f"/media/zoueinj/local_dataset/motion_estimation/{name}", exist_ok=True)
        os.makedirs(f"/media/zoueinj/local_dataset/motion_estimation/{name}/{file}", exist_ok=True)

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        print("Error opening video stream or file")

    json_file = read_json_file(f"output/json/{file}.json")

    total_frames = len(json_file)

    reference_dict, golden_frames = reference_mapping(0, gop, 0, [])

    ret, prev_frame = cap.read()
    prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2YCrCb)

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

        if dataset:

            dataset_stack = None
            for layer in layers:

                if layer == "curr_frame":
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_YCrCb2RGB)
                    dataset_stack = update_stack(dataset_stack, frame_rgb)
                elif layer == "og_frame":
                    frame_rgb = cv2.cvtColor(prev_frame, cv2.COLOR_YCrCb2RGB)
                    dataset_stack = update_stack(dataset_stack, frame_rgb)
                elif layer == "curr_frame_y":
                    dataset_stack = update_stack(dataset_stack, frame[:, :, 0])
                elif layer == "og_frame_y":
                    dataset_stack = update_stack(dataset_stack, prev_frame[:, :, 0])
                elif layer == "mv":
                    dataset_stack = update_stack(dataset_stack, motion_field)
                elif layer == "mv_proj":
                    dataset_stack = update_stack(dataset_stack, motion_field_projection)
                elif layer == "ref":
                    dataset_stack = update_stack(dataset_stack, reference_map)

        stack = np.zeros((height, width, 3), dtype=np.float32)

        stack[:, :, 0] = frame[:, :, 0]/255.
        stack[:, :, 1] = motion_field_projection[:, :, 0]
        stack[:, :, 2] = motion_field_projection[:, :, 1]

        if display:
            cv2.imshow(file, proj_rgb)
            cv2.waitKey(10)

        if forward:
            frame_id = total_frames - 1 - cursor

        else:
            frame_id = cursor

        cv2.imwrite(f"output/results/{file}/pngs/projection/{str(frame_id).zfill(6)}_motion_projection.png", proj_rgb)
        cv2.imwrite(f"output/results/{file}/pngs/reference/{str(frame_id).zfill(6)}_reference_map.png", reference_map)
        cv2.imwrite(f"output/results/{file}/pngs/mv/{str(frame_id).zfill(6)}_motion_field.png", mv_rgb)
        np.save(f"output/results/{file}/npy/mv/{str(frame_id).zfill(6)}_motion_field.npy", motion_field)
        np.save(f"output/results/{file}/npy/mv_proj/{str(frame_id).zfill(6)}_motion_field_projection.npy", motion_field_projection)
        np.save(f"output/results/{file}/stack/{str(frame_id).zfill(6)}_reference_map.npy", stack)

        if dataset:
            np.save(f"/media/zoueinj/local_dataset/motion_estimation/{name}/{file}/{str(frame_id).zfill(6)}_stack.npy", dataset_stack)

        prev_frame = frame.copy()

    cv2.destroyAllWindows()
