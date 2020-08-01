from jtop import jtop
import sys
import os
import threading
import time

# example: 'python3 recorder.py .2 cat sample.txt'
# will run 'cat sample.txt' and log every .2 seconds jtop data

open('log.txt', 'a').write('\n--\n')


def stats_parse(stats):
        time = stats['time'].strftime("%m/%d/%Y, %H:%M:%S:%f")
        cpus = []
        for key in stats:
                if key.startswith('CPU'):
                        cpus.append(stats[key])
        gpu = stats['GPU']
        fan = stats['fan']
        ao_temp = stats['Temp AO']
        cpu_temp = stats['Temp CPU']
        gpu_temp = stats['Temp GPU']
        pll_temp = stats['Temp PLL']
        thermal = stats['Temp thermal']
        current_pwr = stats['power cur']
        avg_pwr = stats['power avg']
        status = '['+time+'] - '
        for i, temp in enumerate(cpus):
                status += 'CPU ' + str(i) + ': ' + str(temp) + '%\t'
        status += 'GPU: ' + str(gpu) + '\tCPU Temp: ' + str(cpu_temp) + '*C\tGPU Temp: ' + str(gpu_temp) + '*C\tThermal: ' + str(thermal) + '*C\tFan: ' + str(fan) + '%\t'
        status += 'Current Power: ' + str(current_pwr) + ' mW\tAverage Power: ' + str(avg_pwr) + 'mW\n'

        return status

class logThread(threading.Thread):
        def __init__(self, event, delay):
                threading.Thread.__init__(self)
                self.e=event
                self.delay=delay

        def run(self):
                with open('log.txt', 'a') as file:
                        with jtop() as jetson:
                                while jetson.ok() and not self.e.isSet():
                                        file.write(stats_parse(jetson.stats))
                                        time.sleep(self.delay)

finished=threading.Event()

log=logThread(finished, float(sys.argv[1]))
log.start()
os.system(' '.join(sys.argv[2:]))
finished.set()
