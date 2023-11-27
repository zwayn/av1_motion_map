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

        command = f"ffmpeg -framerate {arg_flags.fps} -pattern_type glob -i './tmp/*.png' -pix_fmt yuv444p " \
                  f"tmp/{name}.y4m"

        subprocess.run(command, shell=True)

        image = cv2.imread("./tmp/frame_000000.png")
        h, w, _ = image.shape

        command = f"./src/enc_scenario/{arg_flags.encoding_preset}.sh ./tmp/{name}.y4m {name} {w} {h} " \
                  f"{arg_flags.fps*1000} {arg_flags.gop}"
        a = subprocess.run(command, shell=True)
        command = f"./aom_build/examples/inspect ./output/ivf/{name}.ivf -mv -r > ./output/json/{name}.json"
        subprocess.run(command, shell=True)

        main(arg_flags.gop, name, f"./tmp/{name}.y4m", w, h)

        subprocess.run("rm -rf ./tmp/*", shell=True)

    subprocess.run("rm -rf ./tmp", shell=True)
