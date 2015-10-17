#A calendar system with a user interface

#Distributed Systems Project 1
#Greg Weil
#Taoran Li

#Run with python 2.7.10
#No arguments right now

import calendar

cal = calendar.Calendar('config/local.cfg', 0)

cal.addAppointment(calendar.Appointment("Test0", 5, 24, 28))
cal.addAppointment(calendar.Appointment("Test1", 3, 24, 28))
cal.addAppointment(calendar.Appointment("Test2", 3, 20, 24))
try:
	cal.addAppointment(calendar.Appointment("TestConflict", 3, 22, 26))
except Exception as e:
	#This should happen
	print("This is a good thing")

print([str(x) for x in cal.getAppointments()])
