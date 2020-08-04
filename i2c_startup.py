import board
import busio
import threading
import time
import adafruit_mcp9808
import struct

i2c = busio.I2C(board.SCL, board.SDA)

temp_addr = 0x20
benchmark_addr = 0x32
thermo = adafruit_mcp9808.MCP9808(i2c)

class tempThread(threading.Thread):
    def __init__(self, delay, addr, temp, i2c):
        threading.Thread.__init__(self, daemon=True)
        self.delay = delay
        self.addr = addr
        self.temp = temp
        self.i2c = i2c

    def run(self):
        try:
            print(self.temp.temperature)
            self.i2c.writeto(self.addr, struct.pack('f',50.5))
            time.sleep(self.delay)
        except Exception:
            print("Encountered an error in temp thread")


while not i2c.try_lock():
    pass

try:
    result = bytearray(1)
    i2c.readfrom_into(benchmark_addr, result)
    code = int.from_bytes(result,"big")

    if code == 0:
        print("running edge detection")
        msg = bytes(b'It is a period of civil war. Rebel spaceships, striking from a hidden base, have won their first victory against the evil Galactic Empire.')
    elif code == 1:
        print("Running Jetson suite")
        msg = bytes(b'It is a dark time for the Rebellion. Although the Death Star has been destroyed, Imperial troops have driven the Rebel forces from their hidden base and pursued them across the galaxy.')
    elif code == 2:
        print("Running Image compression")
        msg = bytes(b'Luke Skywalker has returned to his home planet of Tatooine in an attempt to rescue his friend Han Solo from the clutches of the vile gangster Jabba the Hutt.')
    elif code == 3:
        print("Runnign Mask R-CNN")
        msg = bytes(b'General Kenobi')
    else:
        print("Unknown code: "+str(code))

    # temp_reading = tempThread(10, temp_addr, thermo)
    # temp_reading.start() 

    time.sleep(3)

    
    msg_size = len(msg)

    i2c.writeto(benchmark_addr, msg)
    read_size = bytearray(8)
    i2c.readfrom_into(benchmark_addr, read_size)
    if len(read_size) == 8:
        val = struct.unpack('L',read_size)
        print(msg_size, val)
    else:
        print("Error reading size")
    
finally:
    i2c.unlock()