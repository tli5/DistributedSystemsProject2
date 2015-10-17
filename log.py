#A generic distributed log framework

import network

class Event:
	def __init__(self, node, time, op):
		self.node = node
		self.time = time
		self.op = op

class Log:
	def __init__(self, config, node):
		self.network = network.Network(config, node)
		self.network.registerReceive(self.receive)
		count = len(self.network.peer)
		self.time = [[0 for i in range(count)] for j in range(count)]
		self.node = node
		self.events = []
		self.update = None
	
	def getTime(self, node = None):
		"""Get the number of events I know a node has"""
		"""Call with no arguments for a local count"""
		if not node:
			node = self.node
		return self.time[self.node][node]
	
	def event(self, op):
		"""Add an event record to the log"""
		self.time[self.node][self.node] += 1
		ev = Event(self.node, self.getTime(), op)
		self.events.append(ev)
	
	def send(self, nodes = None):
		"""Send an updated copy of the log to nodes"""
		if not nodes:
			nodes = range(len(self.network.peer))
		self.network.send("Hello!", nodes)
	
	def receive(self, node, message):
		"""We've received something from a node"""
		print(node, message)
		if self.update: self.update()
	
	def registerUpdate(self, func):
		"""Register a function to call when we get an updated log"""
		self.update = func
