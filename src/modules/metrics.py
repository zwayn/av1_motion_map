"""
 metrics.py

  Created by Julien Zouein on 04/12/2023.
  Copyright © 2023 Sigmedia.tv. All rights reserved.
  Copyright © 2023 Julien Zouein (zoueinj@tcd.ie)
----------------------------------------------------------------------------

Python file used to define all the metrics used to evaluate the quality of the extracted motion vectors.
"""

import sys

import numpy as np
import tensorflow as tf

from ..third_party.flowpy.flowpy import forward_warp


this_module = sys.modules[__name__]


def end_point_error(motion_vectors: np.ndarray, ground_truth: np.ndarray) -> float:
    """
    Compute the end-point error between the motion vectors and the ground truth.
    :param motion_vectors: motion vectors to evaluate.
    :param ground_truth: ground truth motion vectors.
    :return: end-point error.
    """
    return np.linalg.norm(motion_vectors - ground_truth)


def interpolation_error(motion_vectors: np.ndarray, current_frame: np.ndarray, next_frame: np.ndarray) -> float:
    """
    Compute the interpolation error between the motion vectors and the ground truth.
    :param motion_vectors: motion vectors to evaluate.
    :param current_frame: current frame.
    :param next_frame: next frame.
    :return: interpolation error.
    """

    interpolated_frame = forward_warp(current_frame, motion_vectors)

    return np.square(np.subtract(next_frame, interpolated_frame)).mean()


def ms_ssim(original_frame: np.ndarray, encoded_frame: np.ndarray) -> float:
    """
    Compute the multi-scale structural similarity index between the current frame and the next frame.
    :param original_frame: Original Frame
    :param encoded_frame: Frame encoded in AV1
    :return: ms-ssim
    Compute the multiscale structural similarity index between the current frame and the next frame.
    :param original_frame: Original Frame.
    :param encoded_frame: Frame encoded in AV1.
    :return: ms-ssim.
    """
    return tf.image.ssim_multiscale(original_frame, encoded_frame, max_val=255).numpy()


def psnr(original_frame: np.ndarray, encoded_frame: np.ndarray) -> float:
    """
    Compute the peak signal-to-noise ratio between the current frame and the next frame.
    :param original_frame: Original Frame.
    :param encoded_frame: Frame encoded in AV1.
    :return: psnr.
    """
    return tf.image.psnr(original_frame, encoded_frame, max_val=255).numpy()


def total_variation(frame: np.ndarray) -> float:
    """
    Compute the total variation of the motion vectors.

    Total Variation can be used as a metric to compute the complexity of a frame. It measures the amount of variation in
     pixel intensity, which can be an indicator of texture or edge complexity.

    :param frame: motion vectors to evaluate.
    :return: total variation.
    """
    return tf.image.total_variation(frame).numpy()


def compute_metrics(
    list_metrics: list,
    original: np.array,
    previous: np.array,
    tested: np.array,
    mv_original: np.array,
    mv: np.array,
    row: list
) -> list:
    """
    Compute metrics based on a list of metrics

    :param list_metrics: list of metrics to compute.
    :param original: original frame, from the original video.
    :param previous: previous frame from the original video.
    :param tested: encoded frame.
    :param mv_original: motion vectors out of AV1.
    :param mv: ground truth motion vectors.
    :param row: the current csv row to complete.
    :return: list of values out of the computed metrics.

    """

    for metric in list_metrics:

        metric_func = getattr(this_module, metric)

        if metric == "total_variation":
            value = metric_func(original)

        elif metric == "end_point_error":
            value = metric_func(mv, mv_original)

        elif metric == "interpolation_error":
            value = metric_func(mv, original, previous)

        else:
            value = metric_func(original, tested)

        row.append(value)

    return row
