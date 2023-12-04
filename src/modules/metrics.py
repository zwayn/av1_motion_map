"""
 metrics.py

  Created by Julien Zouein on 04/12/2023.
  Copyright © 2023 Sigmedia.tv. All rights reserved.
  Copyright © 2023 Julien Zouein (zoueinj@tcd.ie)
----------------------------------------------------------------------------

Python file used to define all the metrics used to evaluate the quality of the extracted motion vectors.
"""

import numpy as np
from ..third_party.flowpy.flowpy import forward_warp


def end_point_error(motion_vectors: np.ndarray, ground_truth: np.ndarray) -> float:
    """
    Compute the end-point error between the motion vectors and the ground truth.
    :param motion_vectors: motion vectors to evaluate
    :param ground_truth: ground truth motion vectors
    :return: end-point error
    """
    return np.linalg.norm(motion_vectors - ground_truth)


def interpolation_error(motion_vectors: np.ndarray, current_frame: np.ndarray, next_frame: np.ndarray) -> float:
    """
    Compute the interpolation error between the motion vectors and the ground truth.
    :param motion_vectors: motion vectors to evaluate
    :param current_frame: current frame
    :param next_frame: next frame
    :return: interpolation error
    """

    interpolated_frame = forward_warp(current_frame, motion_vectors)

    return np.square(np.subtract(next_frame, interpolated_frame)).mean()

