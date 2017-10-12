#!/usr/bin/env python

'''write_schedule.py: Create a dynamic schedule.'''

#from subprocess import call
import os
import stat
import sys

tab = []

with open('events_schedule', 'r') as f:
    for line in f:
        tab.append(line.split(","))

time = [elem[0] for elem in tab]

# format time for output 7 minutes before start of race            
ante_post = 7 # time to set strategy in minutes before race
total_mins = [int(elem[0:2])*60 + int(elem[3:]) - ante_post for elem in time]
schedule_hour = [elem//60 for elem in total_mins]
schedule_minute = [elem%60 for elem in total_mins]
schedule_time = []

for i in range(len(schedule_hour)):
    if(schedule_minute[i]<10):
        schedule_time.append(str(schedule_hour[i])+':0'+str(schedule_minute[i]))
    else:
        schedule_time.append(str(schedule_hour[i])+':'+str(schedule_minute[i]))

'''Before we schedule these programs to be executed by the operating system, 
they are grouped to a single executable file betfair_price_fetcher'''
with open('execute_schedule', 'w+') as f:
    for time in schedule_time:
        f.write('at -f "PATH_TO_betfair_price_fetcher" ' + time + ';\n')

#call(['chmod', 'u+rwx', '/home/bs/betfair/execute_schedule'])
os.chmod('execute_schedule', stat.S_IRWXU)