#A distributed calendar system

import log

class Appointment:
	def __init__(self, name, day, start, end, members):
		self.name = name
		self.members = members
		self.day = day
		self.start = start
		self.end = end
	
	def __str__(self):
		return str((self.name, self.members, self.day, self.start, self.end))
	
	def checkConflict(self, other):
		"""Check if this event conflicts with another"""
		if (self.day != other.day):
			return False
		if (self.start >= other.end):
			return False
		if (self.end <= other.start):
			return False
		return True

class Calendar:
	def __init__(self, config, node):
		self.log = log.Log(config, node)
		self.node = node
	
	def getAppointments(self):
		"""Get a list of all appointments in the local calendar"""
		"""Order is completely arbitrary"""
		opAdd = [e.op for e in self.log.events if isinstance(e.op, Appointment)]
		opDel = [e.op for e in self.log.events if isinstance(e.op, basestring)]
		appointments = [op for op in opAdd if op.name not in opDel]
		return [apt for apt in appointments if self.node in apt.members]
	
	def addAppointment(self, apt):
		"""Add an appointment to the calendar"""
		"""If other users are a member, they will be notified"""
		if self.checkConflicts(apt):
			raise Exception('conflict')
		self.log.event(apt)
		self.log.send(apt.members)
	
	def removeAppointment(self, apt):
		"""Remove an event from the calendar"""
		"""If other users are members, they will be notified"""
		self.log.event(apt.name)
		self.log.send(apt.members)
	
	def checkConflicts(self, apt):
		"""Check if an appointment conflicts with the local calendar"""
		for check in self.getAppointments():
			if apt.checkConflict(check):
				return True
		return False
