#A distributed calendar system

import paxosnew

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
	return isinstance(e, dict)
def eventIsDel(e):
	"""This log event removes an appointment"""
	return isinstance(e, basestring)

class Calendar(object):
	def __init__(self, config, node, paxos):
		self.paxos = paxos
		self.node = node
	
	def getAppointments(self, node = None):
		"""Get a list of all appointments in the local calendar"""
		"""Order is completely arbitrary"""
		if node == None:
			node = self.node
		opAdd = [aptLoad(e) for e in self.paxos.retrieveLog() if eventIsAdd(e)]
		opDel = [e for e in self.paxos.retrieveLog() if eventIsDel(e)]
		appointments = [op for op in opAdd if op.name not in opDel]
		return [apt for apt in appointments if node in apt.members]
	
	def getAppointmentsByNodes(self):
		"""Get a list of appointments for each node acknowledged by the current node"""
		peerCount = len(self.paxos.network.peer)
		return [self.getAppointments(i) for i in range(peerCount)]

	def addAppointment(self, apt):
		"""Add an appointment to the calendar"""
		"""If other users are a member, they will be notified"""
		if self.checkConflicts(apt):
			raise Exception('conflict')
		#self.log.event(aptSave(apt))
		#self.log.send(apt.members)
		self.paxos.propose(aptSave(apt))

	def removeAppointment(self, apt):
		"""Remove an event from the calendar"""
		"""If other users are members, they will be notified"""
		#self.log.event(apt.name)
		#self.log.send(apt.members)
		self.paxos.propose(apt.name)

	def checkConflicts(self, apt):
		"""Check if an appointment conflicts with the local calendar"""
		for other in self.getAppointments():
			if apt == other:
				continue
			if apt.checkConflict(other):
				return other
		return None