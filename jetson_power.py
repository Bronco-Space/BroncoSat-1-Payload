import board
import digitalio
import time

# Contains a series of helper functions pertaining to the jetson's power control

rst = digitalio.DigitalInOut(board.PA19)
rst.direction = digitalio.Direction.OUTPUT
rst.value = True

pwr = digitalio.DigitalInOut(board.DAC0)
pwr.direction = digitalio.Direction.OUTPUT
pwr.value = True

def restart():
    rst.value = False
    time.sleep(1)
    rst.value = True

def poweron():
    pwr.value = False
    time.sleep(1)
    pwr.value = True

def poweroff():
    pwr.value = False
    time.sleep(10)
    pwr.value = True