#!/bin/bash

facilities=(1 2)

for facility in "${facilities[@]}"; do
    py kmeanspp.py -f "$facility" > "data/results/$facility-output.txt"
done