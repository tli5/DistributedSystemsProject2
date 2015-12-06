import sys, time
import network
import leader
import pickle
import collections 
import calendar
from pprint import pformat

class Paxos(object):
	def __init__(self, cal):
		nodeNetwork = cal.log.network

		self.leaderNetwork = leader.LeaderNetwork(nodeNetwork)
		self.network = nodeNetwork
		self.node = nodeNetwork.node
		self.network.registerReceive(self.udpReceive)
		self.calendar = cal
		self.path = ('paxos' + str(node) + '.sav')

		"""used when current node serves as a proposer"""
		hd = open(self.path, "rb")
		status = pickle.load(hd)

		"""load backup if exists"""
		try:
		    hd = open(self.path, "rb")
		    status = pickle.load(hd)

		    if ((status is not None) and (status.maxPrepareNum is not None) ) :
		    	self.maxPrepareNum = status.maxPrepareNum
		    	self.prepareNum = status.prepareNum
		    	self.accNum = status.accNum
		    	self.accVal = status.accVal
		    else :
		    	self.maxPrepareNum = self.prepareNum = 0
		    	self.accNum = self.accVal = None
		except IOError:
		    self.maxPrepareNum = self.prepareNum = 0
		    self.accNum = self.accVal = None

		

	"""I probably should have refactored below codes using Enum with each value associated with a function"""
	"""I didn't cause there's not much time left to do the research on syntax issues"""
	def sendPrepare(self) :
		data = object()
		data.type = "prepare"
		data.prepareNum = self.prepareNum
		self.prepareNum += 1
		"""set response count to 0 every time the proposer tries to propose something"""
		self.promises = []
		self.network.send(data)

	def sendPromise(self, val) :
		data = object()
		data.val = val
		data.type = "promise"
		self.network.send(data)

	def sendAccept(self, val) :
		data = object()
		data.val = val
		data.type = "accept"
		self.network.send(data)

	def sendAck(self, val) :
		data = object()
		data.val = val
		data.type = "ack"
		self.network.send(data)

	def sendCommit(self, val) :
		data = object()
		data.val = val
		data.type = "commit"
		self.network.send(data)
		record(data.chosen)

	def draftProposal(self, data) :
		self.proposalVal = data.val
		sendPrepare()

	def receivePrepare(self, data) :
		if (data.prepareNum > self.maxPrepareNum ) :
			self.maxPrepareNum = data.prepareNum
			val = object()
			val.accNum = self.accNum
			val.accVal = self.accVal
			sendPromise(val)
		else :
			data = object()
			data.type = "lowPrepareNum"
			data.val = self.maxPrepareNum
			self.network.send(data)

	def receivePromise(self, data) :
		majority = len(self.network.peer) / 2 + 1
		self.promises.append(data.val)

		count = 0
		lgPromise = None

		for promise in self.promises:
			count += 1
			if (promise.accNum is not None ):
				if (lgPromise is None ) :
					lgPromise = promise
				elif (lgPromise.accNum < promise.accNum ) :
					lgPromise = promise 

		if (count >= majority ) :
			if (lgPromise is not None ):
				val = object()
				val.accNum = promise.accNum
				val.accVal = promise.accVal
				sendAccept(val)
			else :
				val = object()
				val.accNum = self.prepareNum
				val.accVal = self.proposalVal
				sendAccept(val)
		

	def receiveAccept(self, data) :
		if (data.prepareNum >= self.maxPrepareNum)  :
			self.chosen = object()
			self.chosen.accNum = data.val.accNum
			self.chosen.accVal = data.val.accVal
			sendAck(self.chosen)


	def receiveAck(self, data) :
		sendCommit(data)

	def receiveCommit(self, data) :
		record(data.chosen)

	def udpReceive(self, node, data) :
		"""save status"""
		self.save()

		if not data.type :
			print "message received in UDP does not conform to expected protocal"
			return
		elif data.type == "prepare" :
			receivePrepare(data)
		elif data.type == "" :
			receivePromise(data)
		elif data.type == "accept" :
			receiveAccept(data)
		elif data.type == "ack" :
			receiveAck(data)
		elif data.type == "commit" :
			receiveCommit(data)
		elif data.type == "propose" :
			draftProposal(data)

		elif data.type == "lowPrepareNum" :
			"""start over"""
			sendPrepare()

		"""save status"""
		self.save()
		return

	def proposeAppointment(aptInfo) :
		leaderNode = leaderNetwork.leader
		data = object()
		data.val = object()
		data.val.apt = aptInfo.apt
		data.val.type = aptInfo.type
		data.type = "propose"
		target = {leaderNode}
		self.network.send(data, target)

	def record(self, chosen) :
		if (chosen.accVal.type == "add" ) :
			apt = chosen.accVal
			conflict = self.calendar.checkConflicts(apt)
			if (conflict is None ) :
				self.calendar.addAppointment(apt)
		else :
			self.calendar.removeAppointment(chosen.accVal.index)
		

	def save(self):
		"""Write the current status to disk"""
		hd = open(self.path, 'wb')
		status = object()
		status.maxPrepareNum 
		status.prepareNum = self.prepareNum
		status.accNum = self.accNum
		status.accVal = self.accVal
		pickle.dump(status, hd )
		hd.close()