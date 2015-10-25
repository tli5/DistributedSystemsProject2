#A generic distributed log framework

import network
from pprint import pformat

class Event(object):
	def __init__(self, node, time, op):
		self.node = node
		self.time = time
		self.op = op
	
	def __str__(self):
		return str((self.node, self.time, str(self.op)))
	
	def __hash__(self):
		return hash((self.node, self.time))
	def __eq__(self, other):
		return hash(self) == hash(other)
	def __ne__(self, other):
		return hash(self) != hash(other)
def evLoad(data):
	return Event(data['node'], data['time'], data['op'])
def evSave(event):
	return (event.__dict__)

class Log(object):
	def __init__(self, config, node):
		self.network = network.Network(config, node)
		self.network.registerReceive(self.receive)
		count = len(self.network.peer)
		self.time = [[0 for i in range(count)] for j in range(count)]
		self.events = set()
		self.node = node
		self.recv = None
		self.path = ('data' + str(node) + '.sav')
		self.load()
		#Update peers
		self.network.send(('req', self.node))
		self.send()
	
	def getTime(self, node = None):
		"""Get the number of events I know a node has"""
		"""Call with no arguments for a local count"""
		if not node:
			node = self.node
		return self.time[self.node][node]
	
	def event(self, op):
		"""Add an event record to the log"""
		self.time[self.node][self.node] += 1
		event = Event(self.node, self.getTime(), op)
		self.events.add(event)
		self.save()
	
	def send(self, nodes = None):
		"""Send an updated copy of the log to nodes"""
		if not nodes:
			nodes = range(len(self.network.peer))
		for node in nodes:
			events = set([e for e in self.events if self.time[node][e.node] < e.time])
			data = ('log', self.time, events)
			self.network.send(data, [node])
	
	def receive(self, node, data):
		"""We've received something from a node"""
		if data[0] == 'log':
			new = (data[2] - self.events)
			#Union their log with ours
			self.events |= data[2]
			#Update known log times
			time = data[1]
			r = range(len(self.network.peer))
			self.time[self.node] = [max(self.time[self.node][j], time[node][j]) for j in r]
			self.time = [[max(self.time[j][m], time[j][m]) for m in r] for j in r]
			#Notify higher level things
			if self.recv: self.recv(node, new)
			#Save everything
			self.save()
		elif data[0] == 'req':
			self.send([data[1]])
	
	def registerReceive(self, func):
		"""Register a function to call when we get an updated log"""
		self.recv = func
	
	def save(self):
		"""Write the current log to disk"""
		f = open(self.path, 'w')
		f.write(pformat(self.time))
		f.write('\n')
		f.write(pformat([evSave(ev) for ev in self.events]))
		f.close()
	
	def load(self):
		try:
			f = open(self.path, 'r')
			data = f.read().split('\n')
			f.close()
			self.time = eval(data[0])
			eventData = eval('\n'.join(data[1:]))
			self.events = set([evLoad(e) for e in eventData])
		except Exception as e:
			count = len(self.network.peer)
			self.time = [[0 for i in range(count)] for j in range(count)]
			self.events = set()
