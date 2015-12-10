#A leader algorithm over the network library

import network

import socket
import threading
import time
import errno

class LeaderNetwork(object):
	def __init__(self, nodeNetwork):
		self.network = nodeNetwork
		self.peer = [network.Peer(peer.ip, peer.port+1) for peer in self.network.peer]
		self.node = self.network.node
		self.exit = False
		#Election state
		self.leader = 0
		self.election = None
		#Create threads
		self.thread = [{} for i in self.peer]
		self.threadAccept = threading.Thread(target = self.acceptThread)
		self.threadAccept.setDaemon(True)
		self.threadAccept.start()
		#Begin an election
		self.electionBegin()
		self.onBecomeLeader = None
	
	def __del__(self):
		self.exit = True
	
	def acceptThread(self):
		"""Accept incoming connections on a separate thread"""
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.settimeout(1)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind(('', self.peer[self.node].port))
		server.listen(len(self.peer))
		while not self.exit:
			try:
				con = server.accept()
				args = (int(con[0].recv(1)), con[0])
				listen = threading.Thread(target = self.listenThread, args = args)
				listen.setDaemon(True)
				listen.start()
			except socket.error as e:
				if e.errno != errno.EWOULDBLOCK:
					#print('accept', e)
					pass
		server.close()
	
	def listenThread(self, node, sock):
		"""Listen for incoming messages for a single socket on a thread"""
		self.thread[node][sock] = threading.currentThread()
		sock.settimeout(1)
		while not self.exit:
			msg = ''
			try:
				c = sock.recv(1)
				while c != '\n':
					msg += c
					c = sock.recv(1)
			except socket.timeout as e:
				continue
			except socket.error as e:
				print(e)
				break
			
			#Handle the message
			if msg: self.tcpReceive(msg, node)
		
		#If this is the leader, start an election
		if (node == self.leader) and not self.electionActive():
			self.electionBegin()
		
		#Shut down the thread
		sock.close()
		del self.thread[node][sock]
	
	
	def tcpSend(self, message, node):
		"""Find a socket for the node and send the message"""
		sent = False
		for sock in list(self.thread[node].keys()):
			try:
				sock.sendall(message+'\n')
			except socket.error as e:
				#print('send', e)
				pass
			else:
				sent = True
				break
		if not sent:
			sock = None
			try:
				sock = socket.create_connection(self.peer[node].addr(), 1)
				sock.sendall(str(self.node))
				sock.sendall(message+'\n')
			except socket.error as e:
				#print('connect', e)
				pass
			else:
				listen = threading.Thread(target = self.listenThread, args = (node, sock))
				listen.setDaemon(True)
				listen.start()
				sent = True
		return sent
	
	def tcpReceive(self, message, node):
		if message == "coordinator":
			self.leader = node
			if self.node < node:
				if not self.electionActive():
					self.electionBegin()
		elif message == "election":
			if self.node < node:
				self.tcpSend("ok", node)
			if not self.electionActive():
				self.electionBegin()
		elif message == "ok":
			if self.election:
				self.election.cancel()
				self.election = None
	
	
	def electionActive(self):
		"""Test if an election is active"""
		return (self.election != None)
	
	def electionBegin(self):
		"""Initiate a leader election"""
		if self.election:
			self.election.cancel()
			self.election = None
		for i in range(self.node):
			self.tcpSend("election", i)
		self.election = threading.Timer(1, self.electionWin)
		self.election.start()
	
	def electionWin(self):
		self.election = None
		for i in range(len(self.peer)):
			self.tcpSend("coordinator", i)
		if self.onBecomeLeader:
			self.onBecomeLeader()
	
	
	def registerReceive(self, func):
		self.network.registerReceive(func)
	
	def send(self, message, targets = None):
		"""The same as network send, but negative indices go to the leader"""
		if targets:
			targets = [self.leader if i < 0 else i for i in targets]
		return self.network.send(message, targets)
