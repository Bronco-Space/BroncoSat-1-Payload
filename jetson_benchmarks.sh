#!/bin/bash

git clone https://github.com/NVIDIA-AI-IOT/jetson_benchmarks.git
cd jetson_benchmarks
mkdir models
sudo sh install_requirements.sh
python3 utils/download_models.py --all --csv_file_path "$PWD"/benchmark_csv/nx-benchmarks.csv --save_dir "$PWD"/models

