"""
 utils.py

  Created by Julien Zouein on 27/11/2023.
  Copyright © 2023 Sigmedia.tv. All rights reserved.
  Copyright © 2023 Julien Zouein (zoueinj@tcd.ie)
----------------------------------------------------------------------------

Functions useful for the whole project.
"""


import os


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
