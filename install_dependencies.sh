#!/bin/bash

# Upgrade pip
python -m pip install --upgrade pip

# Install PyTorch CPU version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
pip install -r requirements.txt 