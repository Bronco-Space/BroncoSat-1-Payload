from jtop import jtop
import sys
import os
import threading
import time

# example: 'python3 recorder.py .2 "cat sample.txt"'
# will run 'cat sample.txt' and log every .2 seconds jtop data
# Made for python3, needs jetson-stats from pip3

# adds space to the log files incase they already exist
open('log.txt','a').write('\n--\n')
open('log.csv','a').write('\nTime,GPU %,Fan %,AO Temp *C,CPU Temp *C,GPU, Temp *C,Thermal *C,Current Pwr mW,Average Pwr mW,CPU %\n')

# Converts the jetson stats to human readable text and a csv string for writing
def stats_parse(stats):
        time = stats['time'].strftime("%m/%d/%Y %H:%M:%S:%f")
        cpus = []                       # We don't know how many CPUs will be on the device so we store their utilizations in a list, the index is the core number
        for key in stats:
                if key.startswith('CPU'):
                        cpus.append(stats[key])
        gpu = str(stats['GPU'])
        fan = str(stats['fan'])
        ao_temp = str(stats['Temp AO'])
        cpu_temp = str(stats['Temp CPU'])
        gpu_temp = str(stats['Temp GPU'])
        thermal = str(stats['Temp thermal'])
        current_pwr = str(stats['power cur'])
        avg_pwr = str(stats['power avg'])
        status = '['+time+'] - '
        for i, temp in enumerate(cpus):                 # Handle string formatting for each cpu
                status += 'CPU ' + str(i) + ': ' + str(temp) + '%\t'
        status += 'GPU: ' + gpu + '\tCPU Temp: ' + cpu_temp + '*C\tGPU Temp: ' + gpu_temp + '*C\tThermal: ' + thermal + '*C\tFan: ' + fan + '%\tCurrent Power: ' + current_pwr + ' mW\tAverage Power: ' + avg_pwr + 'm W\n'
        csv = ','.join([time, gpu, fan, ao_temp, cpu_temp, gpu_temp, thermal, current_pwr, avg_pwr, ','.join([str(x) for x in cpus])])+'\n'
        return (csv, status)            # Return a tuple with the csv string and human readable string

# Logging thread to run in the background while the command is executing
class logThread(threading.Thread):
        def __init__(self, event, delay):
                threading.Thread.__init__(self)
                self.e = event
                self.delay = delay

        # When the thread starts the log files are opened and a Jtop session is opened. The data is read and written, then the thread sleeps
        def run(self):
                with open('log.txt', 'a') as file:
                        with jtop() as jetson:
                                while jetson.ok() and not self.e.isSet():
                                        with open('log.csv','a') as csv:
                                                (csv_data, string) = stats_parse(jetson.stats)
                                                csv.write(csv_data)
                                                file.write(string)
                                                time.sleep(self.delay)

# Create the event for when the command is done executing
finished = threading.Event()

# Start the logging thread and run the task, trigger the event when the task is done, ending the logging thread
log = logThread(finished, float(sys.argv[1]))
log.start()
os.system(' '.join(sys.argv[2:]))
finished.set()
