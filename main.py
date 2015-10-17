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

cal.addAppointment(calendar.Appointment("Test0", 5, 24, 28, [node]))
cal.addAppointment(calendar.Appointment("Test1", 3, 24, 28, [node]))
cal.addAppointment(calendar.Appointment("Test2", 3, 20, 24, range(len(cal.log.network.peer))))

time.sleep(5)
print([str(x) for x in cal.getAppointments()])

while True:
	time.sleep(0)
