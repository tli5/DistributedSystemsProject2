#A generic distributed network framework

class Peer:
	def __init__(self, ip, port):
		self.ip = str(ip)
		self.port = int(port)
	
	def __str__(self):
		return self.ip + ':' + str(self.port)

class Network:
	def __init__(self, config, node):
		self.peer = []
		self.node = node
		self.recv = None
		self.loadConfig(config)
	
	def loadConfig(self, path):
		f = open(path, 'r')
		for l in f.read().split('\n'):
			if l:
				d = l.split(':')
				self.peer.append(Peer(d[0], d[1]))
	
	def registerReceive(self, func):
		self.recv = func
	
	def send(self, msg, target = None):
		if not target:
			target = range(len(self.peer))
		target = [self.peer[i] for i in target if i != self.node]
		for p in target:
			pass
