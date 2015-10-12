#A generic distributed log framework
#Note that this library does no communication on its own
#It will just tell you what needs to be sent

class Event:
	def __init__(self, node, time, op):
		self.node = node
		self.time = time
		self.op = op

class Log:
	def __init__(self, node, count):
		self.events = []
		self.time = [[0 for i in range(count)] for j in range(count)]
		self.node = node
	
	def getTime(self, node=None):
		"""Get the number of events I know a node has"""
		"""Call with no arguments for a local count"""
		if (node == None):
			node = self.node
		return self.time[self.node][node]
	
	def event(self, op):
		self.time[self.node][self.node] += 1
		ev = Event(self.node, self.getTime(), op)
		self.events.append(ev)
