from utils import utilities, read_write_data, run_benchmark_models
import sys
import warnings
import params as args
import inception_benchmark
import vgg_benchmark
import superres_benchmark
import unet_benchmark
import pose_benchmark
import yolo_benchmark
import resnet_benchmark
import mobilenet_benchmark

logging_delay = args.logging_delay

warnings.simplefilter("ignore")

def run():
    csv_file_path = args.csv_file_path
    model_path = args.model_dir
    precision = args.precision

    # System Check
    system_check = utilities(jetson_devkit=args.jetson_devkit, gpu_freq=args.gpu_freq, dla_freq=args.dla_freq)
    if system_check.check_trt():
        sys.exit()
    system_check.set_power_mode(args.power_mode, args.jetson_devkit)
    system_check.clear_ram_space()
    system_check.run_set_clocks_withDVFS()
    system_check.set_jetson_fan(255)
    benchmark_data = read_write_data(csv_file_path=csv_file_path, model_path=model_path)

    # Run through all the benchmarks here
    running_total = 0
    running_total += inception_benchmark.run()
    running_total += vgg_benchmark.run()
    running_total += superres_benchmark.run()
    running_total += unet_benchmark.run()
    running_total += pose_benchmark.run()
    running_total += yolo_benchmark.run()
    running_total += resnet_benchmark.run()
    running_total += mobilenet_benchmark.run()
    average_fps = running_total/8

    system_check.clear_ram_space()
    system_check.set_jetson_fan(0)
    return average_fps

