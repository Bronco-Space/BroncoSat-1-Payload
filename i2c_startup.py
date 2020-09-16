import board
import busio
import threading
import time
import adafruit_mcp9808
import struct
import record

# import the benchmarks here
import bench_test

i2c = busio.I2C(board.SCL, board.SDA)

temp_addr = 0x20
benchmark_addr = 0x32
thermo = adafruit_mcp9808.MCP9808(i2c)

class tempThread(threading.Thread):
    def __init__(self, delay, addr, temp, i2c, end):
        threading.Thread.__init__(self)
        self.delay = delay
        self.addr = addr
        self.temp = temp
        self.i2c = i2c
        self.e = end

    def run(self):
        while not self.e.isSet():
            try:
                time.sleep(self.delay)
                temp_reading = self.temp.temperature 
                print(temp_reading, temp_reading*9/5+32)
                self.i2c.writeto(self.addr, struct.pack('f',temp_reading))
                
            except Exception:
                print("Encountered an error in temp thread")


while not i2c.try_lock():
    pass

code = 255

try:
    while code > 4:
        result = bytearray(1)
        i2c.readfrom_into(benchmark_addr, result)
        code = int.from_bytes(result,"big")

    i2c.unlock()

    done = threading.Event()

    temp_reading = tempThread(2, temp_addr, thermo, i2c, done)
    temp_reading.start() 

    if code == 0:
        print("running edge benchmark tester")
        msg = record.execute(bench_test)
    elif code == 1:
        print("Running Jetson suite")
        msg = msg = struct.pack('IHffffI',0,0,0,0,0,0,0)
    elif code == 2:
        print("Running Image compression")
        msg = struct.pack('IHffffI',0,0,0,0,0,0,0)
    elif code == 3:
        print("Runnign Mask R-CNN")
        msg = msg = struct.pack('IHffffI',0,0,0,0,0,0,0)
    else:
        print("Unknown code: "+str(code))
        
    done.set()
    temp_reading.join()

    while not i2c.try_lock():
        pass

    i2c.writeto(benchmark_addr, msg)
    recieved = bytearray(28)
    i2c.readfrom_into(benchmark_addr, recieved)
    val = struct.unpack('IHffffI', recieved)
    print(msg, recieved)

finally:
    i2c.unlock()