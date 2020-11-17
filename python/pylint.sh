#!/bin/bash

clear

python3 -m pylint stats.py --rcfile=.pylintrc
python3 -m pylint helpers --rcfile=.pylintrc
