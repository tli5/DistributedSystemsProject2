#A leader algorithm over the network library

import network

import socket
import threading
import errno
import time

class LeaderNetwork(object):
	def __init__(self, network):
		self.network = network
		self.leader = 0
		#TCP connection data
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind(self.network.peer[self.network.node].addr())
		self.server.listen(self.network.node+1)
		self.server.settimeout(0.0)
		self.socket = [None for i in self.network.peer]
		#Create a thread
		self.threadListen = threading.Thread(target = self.listen)
		self.threadListen.setDaemon(True)
		self.threadListen.start()
		self.threadConnect = threading.Thread(target = self.connect)
		self.threadConnect.setDaemon(True)
		self.threadConnect.start()
	
	def listen(self):
		while True:
			#Check for incoming messages
			for i, sock in enumerate(self.socket):
				if not sock: continue
				try:
					data = sock.recv(4)
					print(data)
				except socket.error as e:
					if e.errno == errno.ECONNRESET:
						self.socket[i] = None
						sock.close()
	
	def connect(self):
		while True:
			#Accept connections from other nodes
			try:
				con = self.server.accept()
				node = int(con[0].recv(1))
				print(node)
				self.socket[node] = con[0]
			except socket.error as e:
				#No connections to accept
				pass
			#Attempt connections to lower numbered nodes
			for i in range(self.network.node):
				if self.socket[i]: continue
				try:
					con = socket.create_connection(self.network.peer[i].addr(), 1.0)
					con.sendall(str(self.network.node))
					self.socket[i] = con
				except socket.error as e:
					#Still down
					pass
	
	def registerReceive(self, func):
		self.network.registerReceive(func)
	
	def send(self, message, targets = None):
		if targets:
			targets = [self.leader if i < 0 else i for i in targets]
		return self.network.send(message, targets)
