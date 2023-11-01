#!/bin/bash

for facility in {1..641..1}; do
	echo "Working on $facility"
    py kmeanspp.py -f "$facility" > "data/results/$facility-output.txt"
done