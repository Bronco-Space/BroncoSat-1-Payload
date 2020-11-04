import board
import busio
import threading
import time
import struct
import record

# import the benchmarks here
import edge_detection_benchmark
import compression_benchmark
import inception_benchmark
import vgg_benchmark
import superres_benchmark
import unet_benchmark
import pose_benchmark
import yolo_benchmark
import resnet_benchmark
import mobilenet_benchmark
import jetson_suite_benchmark


i2c = busio.I2C(board.SCL, board.SDA)

temp_addr = 0x20
benchmark_addr = 0x32

while not i2c.try_lock(): # Acquire the i2c lock
    pass

code = 255

print("Starting i2c_startup.py...")

try:
    # Reads the benchmark code from I2C until a valid code appears. Then send 10.5 to signal to the pycubed that it is starting the benchmark
    while code > 20:
        result = bytearray(1)
        i2c.readfrom_into(benchmark_addr, result)
        code = int.from_bytes(result,"big")
        print("invalid code: ",code)
    i2c.writeto(temp_addr, struct.pack('f',10.5))
    i2c.unlock()

    if code == 0:
        print("Running Edge Detection")
        msg = record.execute(edge_detection_benchmark)
    elif code == 1:
        print("Running Image compression")
        msg = record.execute(compression_benchmark)
    elif code == 2:
        print("Running Inception")
        msg = record.execute(inception_benchmark)
    elif code == 3:
        print("Running VGG19")
        msg = record.execute(vgg_benchmark)
    elif code == 4:
        print("Running Super Resolution")
        msg = record.execute(superres_benchmark)
    elif code == 5:
        print("Running UNET")
        msg = record.execute(unet_benchmark)
    elif code == 6:
        print("Running Pose Estimation")
        msg = record.execute(pose_benchmark)
    elif code == 7:
        print("Running YOLO V3")
        msg = record.execute(yolo_benchmark)
    elif code == 8:
        print("Running Resnet")
        msg = record.execute(resnet_benchmark)
    elif code == 9:
        print("Running Mobilenet V1")
        msg = record.execute(mobilenet_benchmark)
    elif code == 10:
        print("Running All Nvidia Benchmarks")
        msg = record.execute(jetson_suite_benchmark)
    else:
        print("Unknown code: "+str(code))
        
        
    while not i2c.try_lock():
        pass
    
    # Once the benchmark finishes the data is packaged into a bytearray and sent over I2C
    
    print('Sending data')
    i2c.writeto(benchmark_addr, msg)
    
    # Verify that the pycubed recieved the same bytearray
    recieved = bytearray(28)
    print(recieved)
    i2c.readfrom_into(benchmark_addr, recieved)
    val = struct.unpack('IHffffI', recieved)
    print(msg, recieved)
except Exception as err:
    print(err)
finally:
    i2c.unlock()
