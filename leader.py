#A leader algorithm over the network library

import network

import socket
import threading
import time
import errno

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
		poll = time.clock()
		#Just connect to everything for now
		self.tcpSend("hoopla", range(len(self.network.peer)))
		while True:
			#Accept connections from other nodes
			while self.tcpAccept(): pass
			#Check for incoming messages
			for i, sock in enumerate(self.socket):
				if not sock: continue
				try:
					data = self.tcpReceive(sock)
					if data: print('received "'+data+'"')
				except socket.error as e:
					print('receive', i, e)
					if e.errno == errno.ECONNRESET or True:
						print('disconnect', i)
						self.socket[i] = None
						sock.close()
			#Confirm the connection is alive
			if time.clock() > poll:
				print('ping')
				for i, sock in enumerate(self.socket):
					if not sock: continue
					self.tcpSend('', [i])
				poll = (time.clock() + 5)
	
	def tcpAccept(self):
		"""Accept an incoming connection"""
		"""This should only be called from the listen thread"""
		try:
			con = self.server.accept()
			node = int(self.tcpReceive(con[0], True))
			if self.socket[node] and node < self.network.node:
				self.socket[node].close()
				self.socket[node] = None
			if not self.socket[node]:
				self.socket[node] = con[0]
				print('connect from ' + str(node))
			else:
				con[0].close()
				print('ignored connect from ' + str(node))
		except socket.error as e:
			#No connections to accept
			if e.errno != errno.EWOULDBLOCK:
				print('accept', e)
			return False
		return True
	
	def tcpSend(self, message, targets):
		"""Send a message to the set of targets"""
		"""Connections will be attempted if not established"""
		"""This should only be called from the listen thread"""
		#Establish connections to other nodes
		for i in targets:
			if i == self.network.node: continue
			if self.socket[i]: continue
			try:
				con = socket.create_connection(self.network.peer[i].addr(), 1.0)
				self.socket[i] = con
				self.tcpSend(str(self.network.node), [i])
				print('connect to ' + str(i))
			except socket.error as e:
				#Still down
				print('con', i, e)
				pass
		#Send the message
		if message != None:
			for i in targets:
				if i == self.network.node: continue
				if not self.socket[i]: continue
				try:
					self.socket[i].settimeout(5.0)
					self.socket[i].sendall(message+'\n')
				except socket.error as e:
					print('send', i, e)
	
	def tcpReceive(self, sock, block = False):
		"""Receive a message on a tcp socket"""
		"""Messages are separated by \n"""
		"""This should only be called from the listen thread"""
		msg = ''
		try:
			sock.settimeout(5.0 if block else 0.0)
			c = sock.recv(1)
			sock.settimeout(1.0)
			while c != '\n':
				msg += c
				c = sock.recv(1)
		except socket.error as e:
			if e.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
				msg = None
			else:
				raise
		except socket.timeout:
			msg = None
		return msg
	
	def registerReceive(self, func):
		self.network.registerReceive(func)
	
	def send(self, message, targets = None):
		if targets:
			targets = [self.leader if i < 0 else i for i in targets]
		return self.network.send(message, targets)
