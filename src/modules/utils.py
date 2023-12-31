"""
 utils.py

  Created by Julien Zouein on 27/11/2023.
  Copyright © 2023 Sigmedia.tv. All rights reserved.
  Copyright © 2023 Julien Zouein (zoueinj@tcd.ie)
----------------------------------------------------------------------------

Functions useful for the whole project.
"""


import os

import csv
import numpy as np

from ..third_party import flowpy


def get_paths(directory: str) -> list:
    """
    Get all the paths of the files in a directory

    :param directory: directory to look into
    :return: list of paths of the files in the directory
    """
    paths = []
    extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".flo"]
    for directory_path, _, filenames in os.walk(directory):
        file_paths = [
            file for file in filenames if any(file.lower().endswith(extension) for extension in extensions)
        ]

        for filename in file_paths:
            paths.append(os.path.join(directory_path, filename))
    paths.sort()

    return paths


def init_csv(output_path: str, complexity_metrics: list, quality_metrics: list, motion_metrics: list) -> None:
    """
    Initialise the CSV file.
    :param output_path: path of the output file
    :param complexity_metrics: list of complexity metrics
    :param quality_metrics: list of quality metrics
    :param motion_metrics: list of motion metrics
    :return: None
    """
    cols = ["frame_number"]
    cols.extend(complexity_metrics)
    cols.extend(quality_metrics)
    for metric in motion_metrics:
        if metric == "end_point_error":
            cols.extend(["epe", "1px", "3px", "5px"])
        else:
            cols.append(metric)
    with open(f"{output_path}/log_metrics.csv", 'a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(cols)


def read_flo(flo_path) -> np.array:
    """
    Read a .flo file

    :param flo_path: path of the .flo file
    :return: a numpy array
    """

    flo_map = flowpy.flow_read(flo_path)
    return flo_map


def update_stack(stack: np.array, layer: np.array):

    if stack is None:
        return layer

    return np.dstack((stack, layer))


def write_csv(output_path: str, row: list) -> None:
    """
    Write a row in the CSV file.
    :param output_path: path of the output file
    :param row: row to write
    :return: None
    """
    with open(f"{output_path}/log_metrics.csv", 'a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(row)
