import board
import busio
import threading
import time
import adafruit_mcp9808
import struct
import record

# import the benchmarks here
import edge_detection_benchmark
import compression_benchmark
import mask_benchmark
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
thermo = None
thermo = adafruit_mcp9808.MCP9808(i2c)      # Uncomment to enable temp reading

class tempThread(threading.Thread):
    def __init__(self, delay, addr, temp, i2c, end):
        print("creating temp thread...")
        threading.Thread.__init__(self)
        self.delay = delay
        self.addr = addr
        self.temp = temp
        self.i2c = i2c
        self.e = end

    def run(self):
        print("starting temp thread")
        while not self.e.isSet():
            try:
                time.sleep(self.delay)
                temp_reading = self.temp.temperature 
                print(temp_reading, temp_reading*9/5+32)
                self.i2c.writeto(self.addr, struct.pack('f',temp_reading))
                
            except Exception as e:
                print("Encountered an error in temp thread",e)


while not i2c.try_lock(): # Acquire the i2c lock
    pass

code = 255

print("starting i2c_startup.py...")

try:
    while code > 20:
        result = bytearray(1)
        i2c.readfrom_into(benchmark_addr, result)
        code = int.from_bytes(result,"big")
        print("invalid code: ",code)

    i2c.unlock()

    done = threading.Event()

    # Create the temperature reading thread with temp reading delay in seconds (first arg)
    if thermo:
        temp_reading = tempThread(15, temp_addr, thermo, i2c, done)
        temp_reading.start() 

    if code == 0:
        print("Running Edge Detection")
        msg = record.execute(edge_detection_benchmark)
    elif code == 1:
        print("Running Image compression")
        msg = record.execute(compression_benchmark)
    elif code == 2:
        print("Running Mask R-CNN")
        msg = record.execute(mask_benchmark)
    elif code == 3:
        print("Running Inception")
        msg = record.execute(inception_benchmark)
    elif code == 4:
        print("Running VGG19")
        msg = record.execute(vgg_benchmark)
    elif code == 5:
        print("Running Super Resolution")
        msg = record.execute(superres_benchmark)
    elif code == 6:
        print("Running UNET")
        msg = record.execute(unet_benchmark)
    elif code == 7:
        print("Running Pose Estimation")
        msg = record.execute(pose_benchmark)
    elif code == 8:
        print("Running YOLO V3")
        msg = record.execute(yolo_benchmark)
    elif code == 9:
        print("Running Resnet")
        msg = record.execute(resnet_benchmark)
    elif code == 10:
        print("Running Mobilenet V1")
        msg = record.execute(mobilenet_benchmark)
    elif code == 11:
        print("Running All Nvidia Benchmarks")
        msg = record.execute(jetson_suite_benchmark)
    else:
        print("Unknown code: "+str(code))
        
        
    done.set()
    
    if thermo:
        temp_reading.join()  # Close the temp thread

    while not i2c.try_lock():
        pass
    print('sending data')
    i2c.writeto(benchmark_addr, msg)
    recieved = bytearray(28)
    print(recieved)
    i2c.readfrom_into(benchmark_addr, recieved)
    val = struct.unpack('IHffffI', recieved)        # Packages data and sends to pycubed
    print(msg, recieved)
except Exception as err:
    print(err)
finally:
    i2c.unlock()
