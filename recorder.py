#!/usr/bin/env python3

from jtop import jtop
import sys
import os
import threading
import time
import getopt
from datetime import datetime

# example: 'python3 recorder.py .2 "cat sample.txt"'
# will run 'cat sample.txt' and log every .2 seconds jtop data
# Made for python3, needs jetson-stats from pip3

# Prints the usage of the script in case there is an error
def usage():
	print('recorder.py usage --\nOptions:')
	print('\t-h  -  Help, brings up this usage text')
	print('\t-d  -  How many seconds to wait between logging the data from jtop [can be any positive float value]')
	print('\t-c  -  The command you wish to run and log data from (NOTE: surround this argument with quotes(")) [ex. "python3 test.py"]')
	print('\t-o  -  (Optional) The name of the log csv (date and time will be appended to the name), defaults to "out" [any valid filename]')
	print('\t-p  -  (Optional) The output directory of the log files, defaults to current directory [path with trailing backslash, ex. /home/user/]')
	print('\t-t  -  (Optional) If specified, the program will run until the original temp is reached, or this timeout (in seconds) is reached, defaults to end after the command is done [any positive float]')
	print('\t-r  -  (Optional) If this flag is present, a human readable text file will be outputted as well')
	print('\t-f  -  (optional) If this flag is present the program will use seconds since startup instead of a formatted date string for time')
	print('\t-s  -  (Optional) If this flag is present, the jetson will shutdown after it is done')


output_name = 'out'
time_dir = datetime.now().strftime('%Y-%m-%d/%H-%M/')
output_dir = os.getcwd()+'/'
timeout = 0
command_str = ''
logging_delay = 1
shutdown = False
output_txt = False
formatted_time = True

# Gets the command line arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], 'hd:c:o:p:t:sfr')
	flags = set([opt[0] for opt in opts])
	opts = dict(opts)
	if '-h' in flags:
		usage()
		exit()
	elif not {'-d', '-c'}.issubset(flags):
		print('-d and and -c are required')
		usage()
		exit()
	elif len(args) > 0:
		print("WARNING: You have extra arguments in this command: " +
			', '.join(args)+'. These will be ignored.')

	logging_delay = float(opts['-d'])
	command_str = opts['-c'].strip()

	output_txt = '-r' in flags
	shutdown = '-s' in flags
	if '-o' in flags:
		output_name = opts['-o'].strip()
	if '-p' in flags:
		output_dir = opts['-p'].strip()
	if '-t' in flags:
		timeout = float(opts['-t'])
	if '-f' in flags:
		formatted_time = False
	output_dir = output_dir+time_dir
	print(output_dir)
	os.makedirs(output_dir, exist_ok=True)
except getopt.GetoptError as err:
	print(str(err))
	exit()

# adds space to the log files incase they already exist
if output_txt:
	open(output_dir+output_name+'.txt', 'w').close()
open(output_dir+output_name+'-console-output.txt', 'w').close()
open(output_dir+output_name+'.csv', 'w').write(
	'Time,GPU %,Fan %,AO Temp *C,CPU Temp *C,GPU Temp *C,Thermal *C,Current Pwr mW,Average Pwr mW,GPU Freqency Hz,CPU %\n')


# Converts the jetson stats and gpu stats to human readable text and a csv string for writing

def stats_parse(stats, gpu_stats):
	if formatted_time:
		time = stats['time'].strftime("%m/%d/%Y %H:%M:%S:%f")
	else:
		time = os.popen('ps -o etimes -fp 1').read().split('\n')[1].strip()
	# We don't know how many CPUs will be on the device so we store their utilizations in a list, the index is the core number
	cpus = []
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
	gpu_freq = str(gpu_stats['frq'])
	status = '['+time+'] - '
	# Handle string formatting for each cpu
	for i, temp in enumerate(cpus):
		status += 'CPU ' + str(i) + ': ' + str(temp) + '%\t'
	status += 'GPU: ' + gpu + '\tCPU Temp: ' + cpu_temp + '*C\t GPU Temp: ' + gpu_temp + '*C\tThermal: ' + \
	thermal + '*C\tFan: ' + fan + '%\tCurrent Power: ' + \
	current_pwr + ' mW\tAverage Power: ' + avg_pwr + 'm W\n'
	csv = ','.join([time, gpu, fan, ao_temp, cpu_temp, gpu_temp, thermal,
			current_pwr, avg_pwr,gpu_freq, ','.join([str(x) for x in cpus])])+'\n'
	# Return a tuple with the csv string and human readable string
	return (csv, status)

# Logging thread to run in the background while the command is executing


class logThread(threading.Thread):
	def __init__(self, event, filename, delay, timeout_sec, make_txt):
		threading.Thread.__init__(self)
		self.e = event
		self.delay = delay
		self.timeout_updates = timeout_sec/delay
		self.start_temp = None
		self.filename = filename
		self.make_txt = make_txt

	# When the thread starts the log files are opened and a Jtop session is opened. The data is read and written, then the thread sleeps
	def run(self):
		try:
			with jtop() as jetson:
				while jetson.ok():
					if self.start_temp is None:
						self.start_temp = jetson.stats['Temp GPU']
					elif self.e.isSet():
						if self.timeout_updates <= 0 or jetson.stats['Temp GPU'] <= self.start_temp:
							break
						self.timeout_updates -= 1
					with open(self.filename+'.csv', 'a') as csv:
						(csv_data, string) = stats_parse(jetson.stats, jetson.gpu)
						csv.write(csv_data)
						if self.make_txt:
							with open(self.filename+'.txt', 'a') as file:
								file.write(string)
						time.sleep(self.delay)
		except KeyboardInterrupt:
			print("Ending recording early...")


# Create the event for when the command is done executing
finished = threading.Event()

# Start the logging thread and run the task, trigger the event when the task is done, ending the logging thread
log = logThread(finished, output_dir+output_name, logging_delay, timeout, output_txt)
log.start()
os.system('script --timing=' + output_dir+output_name + '-times.txt '+output_dir+output_name+'-console-output.txt -c "'+command_str+'"')
#os.system(command_str)

finished.set()
#print('Done all')

if shutdown:
	print("Shutting down...")
	os.system('sudo shutdown -h now')
