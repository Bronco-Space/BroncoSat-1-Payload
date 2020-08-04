import board 
import digitalio
#import jetson_power
from i2cslave import I2CSlave
import time
import struct
# from pycubed import cubesat  #TODO: make cubesat.py without the i2c/spi
import os, storage
import adafruit_sdcard

# Possible benchmark codes:
# 0 - Edge detection
# 1 - Jetson suite
# 2 - Image compression
# 3 - Mask R-CNN
# 4 - ???

def help():
    print('Possible benchmark codes:\n\t0 - Edge detection\n\t1 - Jetson suite\n\t2 - Image compression\n\t3 - Mask R-CNN\n\t4 - ???')

benchmark_addr = 0x32
temp_addr = 0x20

# jetson_pwr.poweroff()

sd_present = False

def read_file(filename='data'):
    with open('/sd/'+filename, 'r') as file:
        for line in file:
            print(line.strip())


def run(code, filename='data'):
    print("Running benchmark with code " + str(code))
    
    with I2CSlave(board.SCK, board.MOSI, [benchmark_addr, temp_addr]) as slave:
        code = bytes([code]) # converts the number to a byte array of size 1
        size = 0
        #jetson_pwr.poweron()
        first_time = True
        jetson_on = True
        while jetson_on:
            r = slave.request()

            if not r:
                # Insert flight computer code here
                print("doing important, blocking work...")
                time.sleep(2)
                continue

            with r: 
                if r.address == temp_addr and not r.is_read: # Runs if the pycubed is contacted on the temperature address
                    recieved = r.read(-1)
                    if len(recieved) == 4: # Verify the temp was sent of the write size
                        temp = struct.unpack('f',recieved)[0]
                        print("Temp read was "+str(temp))
                        # Pass temp into the regulate temp function

                elif r.address == benchmark_addr: # Runs if the pycubed is contacted on the benchmark channel
                    if not r.is_read: # Data to send if the master is sending data
                        recieved = r.read(-1)
                        size = len(recieved)
                        if sd_present:
                            with open('/sd/'+filename,'wb') as file:
                                file.write(recieved)
                            print("Wrote out data to "+filename)
                        else:
                            print(recieved)
                            try:
                                print(struct.unpack('IHffffI',recieved))
                            except Exception:
                                print("Error unpacking bytes")
                            print("No SD card present")
                        print("Exitting loop, data recieved")
                        #jetson_pwr.poweroff()
                        
                    elif r.is_read: # Executes if the master is trying to read from the pycube
                        if size == 0:
                            r.write(code) # Tells the jetson to run the benchmark of the given code
                        else:
                            r.write(recieved) # Write the size of the file recieved to master (in long format, may need to change this), should probaly be replaced with checksum
                            jetson_on = False
    print("clean exit")