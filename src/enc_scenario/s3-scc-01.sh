#!/bin/bash

input=$1
output=$2
width=$3
height=$4
fps=$5
GOP=$6
CPU=$7

if [ $CPU < 7 ]; then
  aom_build/aomenc --verbose --codec=av1 -v --psnr --ivf --frame-parallel=0 \
  --cpu-used=$CPU --passes=1 --end-usage=q --use-fixed-qp-offsets=1 \
  --deltaq-mode=0 --enable-tpl-model=0 --enable-keyframe-filtering=1 \
  --fps=$fps/1000 --input-bit-depth=10 --bit-depth=10 -w $width -h $height \
  --cq-level=27  --tile-columns=0 --threads=1 --min-gf-interval=$GOP \
   --max-gf-interval=$GOP --gf-min-pyr-height=5 --gf-max-pyr-height=5 \
   --kf-min-dist=9999 --kf-max-dist=9999 --lag-in-frames=0 \
   --tune-content=screen -o output/ivf/$output.ivf $input
else
    aom_build/aomenc --verbose --codec=av1 -v --psnr --ivf --frame-parallel=0 \
  --cpu-used=$CPU --passes=1 --end-usage=q --use-fixed-qp-offsets=1 \
  --deltaq-mode=0 --enable-tpl-model=0 --enable-keyframe-filtering=1 \
  --fps=$fps/1000 --input-bit-depth=10 --bit-depth=10 -w $width -h $height \
  --cq-level=27  --tile-columns=0 --threads=1 --min-gf-interval=$GOP \
   --max-gf-interval=$GOP --gf-min-pyr-height=5 --gf-max-pyr-height=5 \
   --kf-min-dist=9999 --kf-max-dist=9999 --lag-in-frames=0 \
   --tune-content=screen --rt -o output/ivf/$output.ivf $input
fi
