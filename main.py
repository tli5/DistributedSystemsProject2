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

cal.addAppointment(calendar.Appointment("Test0", 5, 24, 28))
cal.addAppointment(calendar.Appointment("Test1", 3, 24, 28))
cal.addAppointment(calendar.Appointment("Test2", 3, 20, 24))
try:
	cal.addAppointment(calendar.Appointment("TestConflict", 3, 22, 26))
except Exception as e:
	#This should happen
	print("This is a good thing")

print([str(x) for x in cal.getAppointments()])

cal.log.network.send('hello!')

while True:
	time.sleep(0)
