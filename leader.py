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
		#Create threads
		self.threadAccept = threading.Thread(target = self.acceptThread)
		self.threadAccept.setDaemon(True)
		self.threadAccept.start()
		self.thread = [{} for i in self.network.peer]
		#Attempt connections
		for i in range(len(self.network.peer)):
			self.tcpSend('hoopla', i)
	
	def acceptThread(self):
		"""Accept incoming connections on a separate thread"""
		while True:
			try:
				con = self.server.accept()
				args = (int(con[0].recv(1)), con[0])
				listen = threading.Thread(target = self.listenThread, args = args)
				listen.setDaemon(True)
				listen.start()
			except socket.error as e:
				if e.errno != errno.EWOULDBLOCK:
					print('accept', e)
	
	def listenThread(self, node, sock):
		"""Listen for incoming messages for a single socket on a thread"""
		self.thread[node][sock] = threading.currentThread()
		while True:
			msg = ''
			try:
				c = sock.recv(1)
				while c != '\n':
					msg += c
					c = sock.recv(1)
			except socket.error as e:
				break
			
			#Handle the message
			if msg: self.tcpReceive(msg, node)
		
		#Shut down the thread
		sock.close()
		del self.thread[node][sock]
	
	def tcpSend(self, message, node):
		"""Find a socket for the node and send the message"""
		sent = False
		for sock in self.thread[node]:
			try:
				sock.sendall(message+'\n')
			except socket.error as e:
				print('send', e)
			else:
				sent = True
				break
		if not sent:
			try:
				sock = socket.create_connection(self.network.peer[node].addr())
				sock.sendall(str(self.network.node))
				sock.sendall(message+'\n')
				listen = threading.Thread(target = self.listenThread, args = (node, sock))
				listen.setDaemon(True)
				listen.start()
			except socket.error as e:
				print('connect', e)
			else:
				sent = True
		return sent
	
	def tcpReceive(self, message, node):
		print(node, message)
	
	def registerReceive(self, func):
		self.network.registerReceive(func)
	
	def send(self, message, targets = None):
		if targets:
			targets = [self.leader if i < 0 else i for i in targets]
		return self.network.send(message, targets)
