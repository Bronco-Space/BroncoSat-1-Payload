from utils import utilities, read_write_data, run_benchmark_models
import sys
import warnings
import params as args
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
    

    system_check.clear_ram_space()
    system_check.set_jetson_fan(0)
    return 0