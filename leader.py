#A leader algorithm over the network library

import network

class LeaderNetwork(object):
	def __init__(self, network):
		self.network = network
		self.leader = 0
		#TCP connection data
		self.server = None
		self.socket = [None for i in self.network.peer]
	
	def registerReceive(self, func):
		self.network.registerReceive(func)
	
	def send(self, message, targets = None):
		if targets:
			targets = [self.leader if i < 0 else i for i in targets]
		return self.network.send(message, targets)
