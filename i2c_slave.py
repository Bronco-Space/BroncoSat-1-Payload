import board
from i2cslave import I2CSlave
import time
import struct

msg = bytes(b'edge detection')

def read():
        with I2CSlave(board.SCK, board.MOSI, [0x32, 0x20]) as slave:
                print("starting")
                while True:
                        r = slave.request()

                        if not r:
                                print("doing important, blocking work...")
                                time.sleep(2)
                                continue

                        with r:  # Closes the transfer if necessary by sending a NACK or feeding the master dummy bytes
                                if r.address == 0x20:
                                        recieved = r.read(-1)
                                        print(recieved, len(recieved))
                                        if len(recieved) == 4:
                                                temp = struct.unpack('f',recieved)[0]
                                                print("Temp read was "+str(temp))
                                elif r.address == 0x32:
                                        if not r.is_read:
                                                recieved = r.read(-1)
                                                print(recieved)
                                                if recieved.decode() == 'Hello there':
                                                        msg = bytes(b'General Kenobi')
                                        elif r.is_read:
                                                r.write(msg)
