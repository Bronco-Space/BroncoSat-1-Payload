import os

csv_file_path = os.path.dirname(os.path.abspath(__file__))+'/jetson_benchmarks/benchmark_csv/tx2-nano-benchmarks.csv'
model_dir = os.path.dirname(os.path.abspath(__file__))+'/jetson_benchmarks/models'
precision = 'fp16'
jetson_devkit = 'nano'
gpu_freq = 921600000 
dla_freq = ''
power_mode = 0
logging_delay = 30