#!/bin/bash

mkdir logs
mkdir output

python filter-data-training.py -np 8 > logs/filter-data-training.log 2>&1
python filter-data-validation.py -np 8 > logs/filter-data-validation.log 2>&1
