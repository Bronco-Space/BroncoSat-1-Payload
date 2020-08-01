
import time
import os

path = os.popen('pwd').read()[:-1]+'/'
with open('run.sh', 'w') as file:
        file.write('#!/bin/sh\npython3 '+path+'recorder.py 1 python3 '+path+'test.py')
os.system('chmod u+x run.sh')

print("Make sure to open crontab with 'crontab -e' and add the line '@reboot sleep 180 && "+path+"run.sh")

print('Test function, waiting 3 seconds')

time.sleep(3)

print('Done with test function')
