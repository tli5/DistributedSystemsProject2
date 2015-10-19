#A calendar system with a user interface

#Distributed Systems Project 1
#Greg Weil
#Taoran Li

#Run with python 2.7.10
#Pass config path and what node index this is
#Example: main.py config/local.cfg 0

import calendar
import random
import sys
import time

config = str(sys.argv[1])
node = int(sys.argv[2])

cal = calendar.Calendar(config, node)

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
