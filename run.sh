#!/bin/bash

# This script is used to run the application
source .venv/bin/activate

# All export
set -a
source .env
set +a

python auslander.py
