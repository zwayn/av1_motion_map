"""
 run.py

  Created by Julien Zouein on 27/11/2023.
  Copyright © 2023 Sigmedia.tv. All rights reserved.
  Copyright © 2023 Julien Zouein (zoueinj@tcd.ie)
----------------------------------------------------------------------------

File used to start the process.
"""

import os
import shutil
import subprocess

import configargparse
import cv2

from src.modules.utils import get_paths
from main import main


parser = configargparse.ArgParser()
parser.add(
    "--config",
    required=False,
    is_config_file=True,
    help="Config file path."
)
parser.add(
    "--batch",
    required=False,
    default=False,
    action="store_true",
    help="If you want to process a batch of videos.",
)
parser.add(
    "--complexity_metrics",
    required=False,
    default=None,
    action="append",
    help="Which Complexity metrics to use. (TV)",
)
parser.add(
    "--dataset",
    required=False,
    default=False,
    action="store_true",
    help="Whether you want to regroup the images in a specific folder to be used as a dataset.",
)
parser.add(
    "--display",
    required=False,
    default=False,
    action="store_true",
    help="Whether to display the generated motion vectors or not.",
)
parser.add(
    "--encoding_preset",
    required=False,
    type=str,
    default="s3-scc-01",
    help="Encoding preset.",
)
parser.add(
    "--forward",
    required=False,
    action="store_true",
    help="Get the forward motion vectors.",
)
parser.add(
    "--fps",
    required=False,
    type=int,
    default=30,
    help="fps of the input video.",
)
parser.add(
    "--frame_step",
    required=False,
    type=int,
    default=1,
    help="Step between frames.",
)
parser.add(
    "--gop",
    required=False,
    type=str,
    default="16",
    help="GOP size.",
)
parser.add(
    "--input",
    required=True,
    help="Path to input folder.",
)
parser.add(
    "--iqa",
    required=False,
    default=None,
    action="append",
    help="Which Quality metrics to use. (PSNR, MS-SSIM)",
)
parser.add(
    "--layers",
    required=False,
    help="How to stack the generated data for the dataset creation. (order is important). "
         "{curr_frame, og_frame, curr_frame_y, og_frame_y, mv, mv_proj, ref}",
    action="append",
    default=['og_frame', 'curr_frame', 'mv_proj'],
)
parser.add(
    "--motion_metrics",
    required=False,
    default=None,
    action="append",
    help="Which Motion metrics to use. (epe, interpolation)",
)
parser.add(
    "--original_mv",
    required=False,
    help="Path to the folder with original motion vectors.",
    default="None"
)
parser.add(
    "--version",
    required=False,
    default=False,
    action="store_true",
    help="Display the version of the Software.",
)

arg_flags = parser.parse_args()

version = "0.1.0"

if __name__ == "__main__":

    if arg_flags.version:

        print(version)
        exit()

    if "epe" in arg_flags.motion_metrics and not arg_flags.original_mv:
        print("you have to specify the path to the original motion vectors.")
        exit()

    if arg_flags.batch:

        files = os.listdir(arg_flags.input)

    else:

        files = [arg_flags.input]

    os.mkdir("./tmp")

    for file in files:

        if arg_flags.batch:
            file_path = os.path.join(arg_flags.input, file)
        else:
            file_path = file

        if arg_flags.forward:
            direction = -1
            start = -1
        else:
            direction = 1
            start = 0

        frame_list = get_paths(file_path)

        for cursor in range(0, len(frame_list), arg_flags.frame_step):

            frame_id = start + (cursor * direction)

            shutil.copyfile(frame_list[frame_id], f"./tmp/frame_{str(cursor).zfill(6)}.png")

        name = file_path.split("/")[-1]
        if not name:
            name = file_path.split("/")[-2]

        if arg_flags.forward:
            name += "_forward"

        else:
            name += "_backward"

        name += f"_{arg_flags.gop}"
        name += f"_{arg_flags.frame_step}"
        name += f"_{arg_flags.encoding_preset}"

        image = cv2.imread("./tmp/frame_000000.png")
        h, w, _ = image.shape

        if not os.path.exists(f"./output/ivf/{name}.ivf"):

            command = f"ffmpeg -framerate {arg_flags.fps} -pattern_type glob -i './tmp/*.png' -pix_fmt yuv444p " \
                      f"tmp/{name}.y4m"

            subprocess.run(command, shell=True)

            command = f"./src/enc_scenario/{arg_flags.encoding_preset}.sh ./tmp/{name}.y4m {name} {w} {h} " \
                      f"{arg_flags.fps*1000} {arg_flags.gop}"
            a = subprocess.run(command, shell=True)

        if not os.path.exists(f"./output/json/{name}.json"):
            command = f"./aom_build/examples/inspect ./output/ivf/{name}.ivf -mv -r > ./output/json/{name}.json"
            subprocess.run(command, shell=True)

        main(
            arg_flags.gop,
            name,
            f"./tmp/{name}.y4m",
            w,
            h,
            arg_flags.forward,
            arg_flags.dataset,
            arg_flags.layers,
            arg_flags.frame_step,
            arg_flags.encoding_preset,
            arg_flags.display,
            arg_flags.interpolate,
        )

        subprocess.run("rm -rf ./tmp/*", shell=True)

    subprocess.run("rm -rf ./tmp", shell=True)
