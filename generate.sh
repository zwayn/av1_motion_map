#!/bin/bash

input=$1
output=$2
width=$3
height=$4
fps=$5
GOP=$6

./src/enc_scenario/s3-scc-01.sh $input $output $width $height $fps $GOP
./aom_build/examples/inspect output/ivf/$output.ivf -mv -r > output/json/$output.json
python3.10 main.py --input $output --height $height --width $width --fps $fps --video $input --GOP $GOP
