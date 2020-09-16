import struct
import numpy as np

def format(row):
    data = row.split(',')
    return [float(val) for val in data]

# Processes a csv file and converts it to byte array of usable data
def process(fname, score):
    data = []
    with open(fname,'r') as file:
        first_line = True
        for row in file:
            if first_line:
                first_line = False
            else:
                data.append(format(row))

    data = np.array(data)
    runtime = int(data[-1,0]-data[0,0])
    benchmark_score = score
    init_cpu_temp = data[0,4]
    init_gpu_temp = data[0,5]
    max_cpu_temp = max(data[:,4])
    max_gpu_temp = max(data[:,5])
    delta_time = runtime/data.shape[0]
    total_power = int(sum([pwr*delta_time for pwr in data[:,7]]))
    return struct.pack('IHffffI', runtime,benchmark_score,init_cpu_temp,init_gpu_temp,max_cpu_temp,max_gpu_temp,total_power)
