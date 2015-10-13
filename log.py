#A generic distributed log framework

class Event:
	def __init__(self, node, time, op):
		self.node = node
		self.time = time
		self.op = op

class Log:
	def __init__(self, node, count):
		self.time = [[0 for i in range(count)] for j in range(count)]
		self.node = node
		self.events = []
		self.update = None
	
	def getTime(self, node=None):
		"""Get the number of events I know a node has"""
		"""Call with no arguments for a local count"""
		if (node == None):
			node = self.node
		return self.time[self.node][node]
	
	def event(self, op):
		"""Add an event record to the log"""
		self.time[self.node][self.node] += 1
		ev = Event(self.node, self.getTime(), op)
		self.events.append(ev)
	
	def notify(self, node):
		"""Send an updated copy of the log to node"""
		if (node == self.node):
			pass
	
	def registerUpdate(self, func):
		"""Register a function to call when we get an updated log"""
		self.update = func
