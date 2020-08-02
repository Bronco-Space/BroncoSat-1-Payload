
import time
import os

# Testing script to create the run.sh file for the starting recorder.py automatically, also used to test recorder.py with a 3 second delay

path = os.popen('pwd').read()[:-1]+'/'
with open('run.sh', 'w') as file:
        file.write('#!/bin/sh\nscript console-output.txt -c \'python3 '+path+'recorder.py 1 "python3 '+path+'test.py"\'')
os.system('chmod u+x run.sh')

# Simple instructiosn for making the script run on after reboot with a 3 min delay
print("Make sure to open crontab with 'crontab -e' and add the line '@reboot sleep 180 && "+path+"run.sh")

print('Test function, waiting 3 seconds')

time.sleep(3)

print('Done with test function')
