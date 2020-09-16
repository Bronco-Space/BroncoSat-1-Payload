#!/usr/bin/env python3

from jtop import jtop
import sys
import os
import threading
import time
from datetime import datetime
import postprocess

# Adapted version of recorder.py designed for running benchmarks

# Converts the jetson stats to human readable text and a csv string for writing
def stats_parse(stats):
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
	csv = ','.join([time, gpu, fan, ao_temp, cpu_temp, gpu_temp, thermal,
			current_pwr, avg_pwr, ','.join([str(x) for x in cpus])])+'\n'
	return csv

# Logging thread to run in the background while the command is executing
class logThread(threading.Thread):
	def __init__(self, event, filename, delay):
		threading.Thread.__init__(self)
		self.e = event
		self.delay = delay
		self.filename = filename

	# When the thread starts the log files are opened and a Jtop session is opened. The data is read and written, then the thread sleeps
	def run(self):
		with jtop() as jetson:
			while jetson.ok():
				if self.e.isSet():
					break
				with open(self.filename, 'a') as csv:
					csv.write(stats_parse(jetson.stats))
					time.sleep(self.delay)

# Function to log output from a particular benchmark
def execute(benchmark):
	if os.path.exists(os.getcwd()+'/data/0'):
		benchmark_num = 1 + [int(num) for num in os.listdir(os.getcwd()+'/data')][-1]
	else:
		benchmark_num = 0
	output_name = os.getcwd()+'/data/'+ str(benchmark_num)+'/out.csv'
	os.makedirs(os.path.dirname(output_name), exist_ok=True)
	logging_delay = benchmark.logging_delay

	# Create the event for when the command is done executing
	finished = threading.Event()

	# Start the logging thread and run the task, trigger the event when the task is done, ending the logging thread
	log = logThread(finished, output_name, logging_delay)
	log.start()
	score = benchmark.run()

	finished.set()

	return postprocess.process(output_name, score)
