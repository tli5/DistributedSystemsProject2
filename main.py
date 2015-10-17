#A calendar system with a user interface

#Distributed Systems Project 1
#Greg Weil
#Taoran Li

#Run with python 2.7.10
#Pass config path and what node index this is
#Example: main.py config/local.cfg 0

import calendar
import sys
import time

config = str(sys.argv[1])
node = int(sys.argv[2])

cal = calendar.Calendar(config, node)

time.sleep(3)

if node == 0:
	cal.addAppointment(calendar.Appointment("Event-0-0", 0, 0, 1, [0]))
	time.sleep(3)
else:
	cal.addAppointment(calendar.Appointment("Event-1-0", 1, 0, 1, [1]))
	time.sleep(3)
	cal.addAppointment(calendar.Appointment("Event-1-1", 0, 0, 1, [0, 1]))

time.sleep(3)
print([a.name for a in cal.getAppointments()])

#while True:
#	time.sleep(0)
