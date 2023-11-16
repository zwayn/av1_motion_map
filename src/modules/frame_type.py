"""
 frame_type.py

  Created by Julien Zouein on 11/14/23.
  Copyright © 2023 Sigmedia.tv All rights reserved.
  Copyright © 2023 Julien Zouein. All rights reserved.

----------------------------------------------------------------------------

A set of functions used to generate a list of frame number for each type at a given time.

AV1 is using for each frame a lot of reference frames. Those frame are referred according to their type (LAST, LAST2,
LAST3, GOLDEN, ...). We define a set of functions to retrieve the frame number for the referenced frames at a given
time. Those functions are based on s3-scc-01 and s3-scc-02 encoding scenarios.
"""


def golden_management(golden_list, golden_number, keyframe, reset=False):
    """ Generate the list of the golden frames to use for a given frame.

    :param golden_list: previous list of golden frames.
    :param golden_number: number of the last golden frame.
    :param keyframe: the value of the last keyframe.
    :param reset: Whether we need to reset
    :return: list of golden frames.
    """

    if reset:

        return [keyframe]

    if len(golden_list) < 4:
        golden_list.append(golden_number)
        return golden_list

    if (len(golden_list) == 4) and (keyframe in golden_list):
        golden_list.append(golden_number)
        golden_list.pop(0)
        return golden_list

    golden_list.append(golden_number)

    return golden_list


def reference_mapping(frame_number: int, gop_size: int, last_keyframe: int, golden_list: list) -> tuple:
    """ Returns a dictionary of frame number for the reference frames at a given time.

    :param frame_number: The number of the current frame.
    :param gop_size: The gop size used during encoding.
    :param last_keyframe: Number of the last key_frame processed.
    :param golden_list: List of golden frames.
    :return: Dictionary of frame number for the reference frames at a given time.
    """
    dict = {
        0: last_keyframe,
        1: last_keyframe,
        2: last_keyframe,
        3: last_keyframe,
        4: last_keyframe,
        5: last_keyframe,
        6: last_keyframe,
        7: last_keyframe,
    }
    if frame_number == last_keyframe:
        golden_list = golden_management(golden_list, last_keyframe, last_keyframe, reset=True)
        return dict, golden_list

    gf_number = (frame_number-last_keyframe) / (gop_size/2)

    if gf_number <= 1:

        dict = {
            0: last_keyframe,
            1: max(last_keyframe, frame_number - 1),
            2: max(last_keyframe, frame_number - 2),
            3: max(last_keyframe, frame_number - 3),
            4: last_keyframe,
            5: max(last_keyframe, frame_number - 4),
            6: max(last_keyframe, frame_number - 5),
            7: max(last_keyframe, frame_number - 6),
        }

        return dict, golden_list

    if (frame_number - 1) % (gop_size / 2) == 0:
        golden_list = golden_management(golden_list, frame_number - 1, last_keyframe)

    if gf_number <= 2:

        number = []
        last_number = frame_number
        for i in range(5):
            new_number = last_number - 1
            if new_number in golden_list:
                last_number = new_number - 1
            else:
                last_number = new_number
            number.append(last_number)

        dict = {
            0: last_keyframe,
            1: number[0],
            2: number[1],
            3: number[2],
            4: golden_list[1],
            5: golden_list[0],
            6: number[3],
            7: number[4],
        }

    elif gf_number <= 3:

        number = []
        last_number = frame_number
        for i in range(4):
            new_number = last_number - 1
            if new_number in golden_list:
                last_number = new_number - 1
            else:
                last_number = new_number
            number.append(last_number)
        dict = {
            0: last_keyframe,
            1: number[0],
            2: number[1],
            3: number[2],
            4: golden_list[2],
            5: golden_list[0],
            6: number[3],
            7: golden_list[1],
        }

    elif gf_number <= 4:

        number = []
        last_number = frame_number
        for i in range(3):
            new_number = last_number - 1
            if new_number in golden_list:
                last_number = new_number - 1
            else:
                last_number = new_number
            number.append(last_number)
        dict = {
            0: last_keyframe,
            1: number[0],
            2: number[1],
            3: number[2],
            4: golden_list[3],
            5: golden_list[0],
            6: golden_list[2],
            7: golden_list[1],
        }

    elif gf_number <= 5:

        number = []
        last_number = frame_number
        for i in range(3):
            new_number = last_number - 1
            if new_number in golden_list:
                last_number = new_number - 1
            else:
                last_number = new_number
            number.append(last_number)
        dict = {
            0: last_keyframe,
            1: number[0],
            2: number[1],
            3: number[2],
            4: golden_list[3],
            5: golden_list[2],
            6: golden_list[1],
            7: golden_list[0],
        }

    else:

        if frame_number - 3 <= golden_list[-1]:

            number = []
            last_number = frame_number
            for i in range(2):
                new_number = last_number - 1
                if new_number in golden_list:
                    last_number = new_number - 1
                else:
                    last_number = new_number
                number.append(last_number)

            dict = {
                0: last_keyframe,
                1: number[0],
                2: number[1],
                3: golden_list[3],
                4: golden_list[4],
                5: golden_list[2],
                6: golden_list[1],
                7: golden_list[0],
            }

        else:
            if len(golden_list) > 4:
                golden_list.pop(0)

            number = []
            last_number = frame_number
            for i in range(3):
                new_number = last_number - 1
                if new_number in golden_list:
                    last_number = new_number - 1
                else:
                    last_number = new_number
                number.append(last_number)

            dict = {
                0: last_keyframe,
                1: number[0],
                2: number[1],
                3: number[2],
                4: golden_list[3],
                5: golden_list[2],
                6: golden_list[1],
                7: golden_list[0],
            }

    return dict, golden_list
