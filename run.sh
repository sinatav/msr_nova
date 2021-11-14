#!/bin/bash

echo $PWD
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python nova_task.py
