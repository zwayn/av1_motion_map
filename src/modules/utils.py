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


def get_paths(directory: str) -> list:
    """
    Get all the paths of the files in a directory
    :param directory: directory to look into
    :return: list of paths of the files in the directory
    """
    paths = []
    extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]
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
    cols.extend(motion_metrics)
    with open(f"{output_path}log_metrics.csv", 'a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(cols)


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
    with open(f"{output_path}log_metrics.csv", 'a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(row)
