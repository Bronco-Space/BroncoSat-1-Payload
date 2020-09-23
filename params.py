import os

csv_file_path = os.getcwd()+'/jetson_benchmarks/benchmark_csv/tx2-nano-benchmarks.csv'
model_dir = os.getcwd()+'/jetson_benchmarks/models'
precision = 'fp16'
jetson_devkit = 'nano'
gpu_freq = 921600000 
dla_freq = ''
power_mode = 0
