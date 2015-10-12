#A distributed calendar system

#Distributed Systems Project 1
#Greg Weil
#Taoran Li

#Run with python 2.7.10
#No arguments right now

class CalendarEvent:
	def __init__(self, name, day, start, end):
		self.name = name
		self.day = day
		self.start = start
		self.end = end
	
	def checkConflict(self, other):
		"""Check if this event conflicts with another"""
		if (self.day != other.day):
			return False
		if (self.start >= other.end):
			return False
		if (self.end <= other.start):
			return False
		return True

ev1 = CalendarEvent("Event1", 1, 24, 28)
ev2 = CalendarEvent("Event2", 1, 28, 30)

print(ev1.checkConflict(ev2))
