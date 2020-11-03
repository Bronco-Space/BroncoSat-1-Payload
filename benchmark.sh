#!/bin/bash

sudo python3 /home/bronco/BroncoSat-1-Payload/recorder.py -d 30 -c "python3 /home/bronco/BroncoSat-1-Payload/jetson_benchmarks/benchmark.py --model_name inception_v4 --csv_file_path /home/bronco/BroncoSat-1-Payload/jetson_benchmarks/benchmark_csv/tx2-nano-benchmarks.csv --model_dir /home/bronco/BroncoSat-1-Payload/jetson_benchmarks/models --jetson_devkit nano --gpu_freq 921600000 --power_mode 0 --precision fp16"
