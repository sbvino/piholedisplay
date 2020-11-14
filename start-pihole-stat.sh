#!/bin/bash
clear
echo "Starting stats dashboard for 2in13b epaper"

cd $(dirname $0)/python

python stats.py
