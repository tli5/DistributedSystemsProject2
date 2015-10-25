#A calendar system with a user interface

#Distributed Systems Project 1
#Greg Weil
#Taoran Li

#Run with python 2.7.10
#Pass config path and what node index this is
#Example: ini.py config/local.cfg 0

import calendar
import random
import sys
import time
import glob
import os

def addAppointment():
	name = raw_input('appointment name:' )
	day = int(raw_input('appointment day:' ))
	start = int(raw_input('appointment start:' ))
	stop = int(raw_input('appointment stop:' ))
	memberStrArr = raw_input('appointment members(format [A B C]):' ).split(' ')
	members = [int(memberStr) for memberStr in memberStrArr ]
	appointment = calendar.Appointment(name, day, start, stop, members)
	try:
		cal.addAppointment(appointment)
		print('inserted appointment: ' + str(appointment))
	except Exception as e:
		print('conflict')

def printTime(time):
	return (str) (time / 2) + ':' + ('00' if time % 2 == 0 else '30')

def showAppointments():
	nodesAppointments = cal.getAppointmentsByNodes()
	DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

	for node in range (len(nodesAppointments) ):
		"""skipping all other nodes' appointments"""
		if node != cal.node:
			continue
		appointments = nodesAppointments[node]
		
		for i in range(len(appointments)):
			appointment = appointments[i]
			print 'Name:', appointment.name, ' (Index:'+str(i)+')'
			print '\ton', DAYS[appointment.day], 'From', printTime(appointment.start), 'To', printTime(appointment.end)
			if len(appointment.members) > 1 :
				print '\tmembers:', str(appointments[i].members )
		print 'Current Node:', node
	return nodesAppointments

def delAppointment():
	print('select an appointment to delete:')
	nodesAppointments = showAppointments()

	if nodesAppointments:
		node = cal.node
		index = int(raw_input('index of appointment to delete:') )
		cal.removeAppointment(nodesAppointments[node][index])
		print('deleted appointment: ' + nodesAppointments[node][index].name)
		print 'current appointments:'
		showAppointments()
	else:
		print('no appointments available')

def clearLog():
	files = glob.glob('./data*.sav')
	for file in files:
		print 'deleting file:', file
		os.remove(file)

def randomTest():
	while True:
		if random.random() < 0.75:
			name = 'Event-' + str(node) + '-' + str(random.randrange(2 ** 64))
			day = random.randrange(7)
			day = random.randrange(7)
			start = random.randrange(47)
			stop = (random.randrange(1, 48-start) + start)
			members = [i for i in range(len(cal.log.network.peer))
				if random.random() < 0.4 or i == node]
			appointment = calendar.Appointment(name, day, start, stop, members)
			try:
				cal.addAppointment(appointment)
				print('add ' + str(appointment))
			except Exception as e:
				print('conflict')
		else:
			appointments = cal.getAppointments()
			if appointments:
				index = random.randrange(len(appointments))
				cal.removeAppointment(appointments[index])
				print('remove ' + appointments[index].name)
			else:
				print('no appointments')
		time.sleep(random.uniform(1, 5))


config = str(sys.argv[1])
node = int(sys.argv[2])

cal = calendar.Calendar(config, node)

while True:
	print 'Menu: ', '1: Add Appointment', '2: Remove Appointment', '3: Clear Log Files', '4: Random Test', '5: Display Appointments'
	option = raw_input('Option:')
	exe = {
	    '1': addAppointment,
	    '2': delAppointment,
	    '3': clearLog,
	    '4': randomTest,
	    '5': showAppointments
	}[option]
	exe()




