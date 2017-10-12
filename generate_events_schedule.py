#!/usr/bin/env python

'''generate_events_schedule.py: Generate event list ordered by time.'''

import time

import pymysql.cursors

date_today = time.strftime("%Y-%m-%d")

connection = pymysql.connect(host='localhost',
                             user='USERNAME',
                             password='YOUR DATABASE PASSWORD',
                             db='DATABASE NAME',
                             charset='utf8mb4',
                             autocommit=True,#connection supposed to closed automatically?
                             cursorclass=pymysql.cursors.DictCursor)

with connection.cursor() as cursor:
    cursor.execute(
        "SELECT DATE_FORMAT(time, '%%H:%%i'), course, marketId FROM races WHERE date = %s ORDER BY time", (date_today))
    markets = cursor.fetchall()
    tab = []
    for market in markets:
        tab.append((market['DATE_FORMAT(time, \'%H:%i\')']+', '+market['course']+', '+market['marketId']+'\n'))

time = []
# sample is for gmt+2
for row in tab:
    # not_dst
    if time.localtime().tm_isdst == 0:
        if(row[0:2] == '19'):
            time.append(('20'+row[2:]))
        elif(row[0:2] == '23'):
            time.append(('00'+row[2:]))
        else:
            time.append((row[0]+str(int(row[1])+1)+row[2:]))
    elif time.localtime().tm_isdst == 1:
    # dst
        if(row[0:2] == '18'):
            time.append(('20'+row[2:]))
        elif(row[0:2] == '19'):
            time.append(('21'+row[2:]))
        elif(row[0:2] == '23'):
            time.append(('01'+row[2:]))
        else:
            time.append((row[0]+str(int(row[1])+2)+row[2:]))
    else:
        pass

with open('events_schedule', 'w+') as f:
    for row in time:
        f.write(row)
