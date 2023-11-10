#!/bin/bash

python3.10 -m pip install -r requirements.txt

git clone https://aomedia.googlesource.com/aom

mkdir aom_build
cd aom_build
cmake ../aom/ -DCONFIG_TUNE_VMAF=1 -DENABLE_CCACHE=1 -DCONFIG_INSPECTION=1
make -j8
