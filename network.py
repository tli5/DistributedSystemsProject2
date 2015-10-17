#A generic distributed network framework

import socket
import threading

class Peer:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
	
	def __str__(self):
		return self.ip + ':' + str(self.port)
	
	def addr(self):
		return (self.ip, self.port)

class Network:
	def __init__(self, config, node):
		self.peer = []
		self.node = node
		self.recv = None
		#Load config
		self.loadConfig(config)
		#Create a socket
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind(self.peer[self.node].addr())
		#Create a thread for the socket
		self.thread = threading.Thread(target = self.listen)
		self.thread.setDaemon(True)
		self.thread.start()
	
	def loadConfig(self, path):
		"""Load the network config file"""
		"""It is a set of addresses separated by newlines"""
		f = open(path, 'r')
		for l in f.read().split('\n'):
			if l:
				d = l.split(':')
				self.peer.append(Peer(d[0], int(d[1])))
	
	def registerReceive(self, func):
		self.recv = func
	
	def listen(self):
		"""Poll the socket for incoming messages"""
		"""Run on a separate thread"""
		while True:
			try:
				data, addr = self.socket.recvfrom(4096)
				for i in range(len(self.peer)):
					if self.peer[i].addr() != addr:
						continue
					self.receive(i, data)
					break
			except socket.error as error:
				pass
	
	def receive(self, node, message):
		"""A message has been received"""
		print(node, message)
	
	def send(self, msg, target = None):
		"""Send a message to some or all peers"""
		if not target:
			target = range(len(self.peer))
		target = [self.peer[i] for i in target if i != self.node]
		for p in target:
			sent = self.socket.sendto(msg, p.addr())
			if sent != len(msg):
				print(send, len(msg))
