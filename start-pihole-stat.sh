#!/bin/bash
echo "Starting stats dashboard for 2in13b epaper"

cd $(dirname $0)/python

sudo python stats.py
