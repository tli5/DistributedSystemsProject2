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
		self.socket = [None for i in self.network.peer]
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind(self.network.peer[self.network.node].addr())
		self.server.listen(len(self.network.peer))
		self.server.settimeout(0.0)
		#Create a thread
		self.threadListen = threading.Thread(target = self.tcpListen)
		self.threadListen.setDaemon(True)
		self.threadListen.start()
	
	def tcpListen(self):
		"""Listen for new connections from other processes"""
		"""This is run on a daemon thread"""
		while True:
			#Accept connections from other nodes
			try:
				con = self.server.accept()
				node = int(con[0].recv(1))
				if self.socket[node]: self.socket[node].close()
				self.socket[node] = con[0]
				print('connect from ' + str(node))
			except socket.error as e:
				#No connections to accept
				pass
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
			#Just connect to everything for now
			self.tcpSend(None, range(len(self.network.peer)))
	
	def tcpSend(self, message, targets):
		"""Send a message to the set of targets"""
		"""Connections will be attempted if not established"""
		"""This should only be called from the listen thread"""
		#Establish connections to other nodes
		for i in targets:
			if self.socket[i]: continue
			try:
				con = socket.create_connection(self.network.peer[i].addr(), 1.0)
				self.socket[i] = con
				self.tcpSend(str(self.network.node), [i])
			except socket.error as e:
				#Still down
				pass
		#Send the message
		if message:
			for i in targets:
				if not self.socket[i]: continue
				self.socket[i].sendall(message+'\n')
		print('sent ' + message)
	
	def registerReceive(self, func):
		self.network.registerReceive(func)
	
	def send(self, message, targets = None):
		if targets:
			targets = [self.leader if i < 0 else i for i in targets]
		return self.network.send(message, targets)
