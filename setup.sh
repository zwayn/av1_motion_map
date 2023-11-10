#!/bin/bash

git clone https://aomedia.googlesource.com/aom

mkdir aom_build
cd aom_build
cmake ../aom/
make -j8
