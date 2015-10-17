#A generic distributed network framework

class Network:
	def __init__(self, node, count):
		self.peer = [None for i in range(count)]
		self.node = node
		self.recv = None
	
	def registerReceive(self, func):
		self.recv = func
	
	def send(self, msg, target = None):
		if not target:
			target = range(len(self.peer))
		target = [self.peer[i] for i in target if i != self.node]
		for p in target:
			pass
