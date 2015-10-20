#A distributed calendar system

import log

class Appointment(object):
	def __init__(self, name, day, start, end, members):
		self.name = name
		self.members = members
		self.day = day
		self.start = start
		self.end = end
	
	def __str__(self):
		return str(aptSave(self))
	
	def __eq__(self, other):
		return self.name == other.name
	
	def checkConflict(self, other):
		"""Check if this event conflicts with another"""
		if (self.day != other.day):
			return False
		if (self.start >= other.end):
			return False
		if (self.end <= other.start):
			return False
		return True
def aptLoad(data):
	return Appointment(data['name'], data['day'],
		data['start'], data['end'], data['members'])
def aptSave(appointment):
	return (appointment.__dict__)

def eventIsAdd(e):
	"""This log event adds an appointment"""
	return isinstance(e.op, dict)
def eventIsDel(e):
	"""This log event removes an appointment"""
	return isinstance(e.op, basestring)

class Calendar(object):
	def __init__(self, config, node):
		self.log = log.Log(config, node)
		self.log.registerReceive(self.receive)
		self.node = node
	
	def getAppointments(self):
		"""Get a list of all appointments in the local calendar"""
		"""Order is completely arbitrary"""
		opAdd = [aptLoad(e.op) for e in self.log.events if eventIsAdd(e)]
		opDel = [e.op for e in self.log.events if eventIsDel(e)]
		appointments = [op for op in opAdd if op.name not in opDel]
		return [apt for apt in appointments if self.node in apt.members]
	
	def addAppointment(self, apt):
		"""Add an appointment to the calendar"""
		"""If other users are a member, they will be notified"""
		if self.checkConflicts(apt):
			raise Exception('conflict')
		self.log.event(aptSave(apt))
		self.log.send(apt.members)
	
	def removeAppointment(self, apt):
		"""Remove an event from the calendar"""
		"""If other users are members, they will be notified"""
		self.log.event(apt.name)
		self.log.send(apt.members)
	
	def checkConflicts(self, apt):
		"""Check if an appointment conflicts with the local calendar"""
		for other in self.getAppointments():
			if apt == other:
				continue
			if apt.checkConflict(other):
				return other
		return None
	
	def receive(self, node, events):
		"""Process a received log for conflicting events"""
		#Check for conflicts in newly added appointments
		for apt in [aptLoad(e.op) for e in events if eventIsAdd(e)]:
			if self.node not in apt.members:
				continue
			conflict = self.checkConflicts(apt)
			if conflict:
				#Keep the event with more members
				if len(apt.members) < len(conflict.members):
					self.removeAppointment(apt)
				elif len(apt.members) > len(conflict.members):
					self.removeAppointment(conflict)
				#Keep the event with a 'lesser' name
				elif apt.name > conflict.name:
					self.removeAppointment(apt)
				elif apt.name < conflict.name:
					self.removeAppointment(conflict)
				#This means two appointments have the same name
				else:
					print("Multiple appointments with name " + apt.name)
		#Check for appointments which can be removed from the log
		evDel = [e for e in self.log.events if eventIsDel(e)]
		evDelRemove = [e for e in evDel if min(self.log.time[:][e.node]) >= e.time]
		aptRemove = [e.op for e in evDelRemove]
		evAdd = [e for e in self.log.events if eventIsAdd(e)]
		evAddRemove = [e for e in evAdd if e.op['name'] in aptRemove]
		for e in set(evAddRemove + evDelRemove):
			self.log.events.remove(e)
		#Save the cleaned log
		self.log.save()
