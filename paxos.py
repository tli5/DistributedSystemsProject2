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
		self.node = nodeNetwork.node
		self.leaderNetwork.registerReceive(self.udpReceive)
		self.path = ('paxos' + str(self.node) + '.sav')

		"""load backup if exists"""
		try:
		    hd = open(self.path, "rb")
		    status = pickle.load(hd)

		    if ((status != None) and (status['maxProposalNum'] != None) ) :
		    	self.maxProposalNum = status['maxProposalNum']
		    	self.proposalNum = status['proposalNum']
		    	self.events = status['events']
		    	self.slot = status['slot']

		    else :
		    	self.maxProposalNum = self.proposalNum = 0
		    	self.events = []
		    	for i in range (0, 20)
		    		self.events.append(None)
		    	self.slot = 0

		except IOError:
		    self.maxProposalNum = self.proposalNum = 0
		    self.events = []
		    for i in range (0, 20)
		    	self.events.append(None)
		    self.slot = 0

		
	"""I probably should have refactored below codes using Enum with each value associated with a function"""
	"""I didn't cause there's not much time left to do the research on syntax issues"""
	def startOver(self, data) :
		self.proposalNum = data['proposalNum']
		self.sendPrepare(data)

	def sendPrepare(self, data) :
		data['type'] = "prepare"
		data['proposalNum'] = self.proposalNum
		self.proposalNum += 1

		"""set response count to 0 every time the proposer tries to propose something"""
		self.promises = []
		self.leaderNetwork.send(data)

	def sendPromise(self, val) :
		data = {}
		data['val'] = val
		data['type'] = "promise"
		self.leaderNetwork.send(data)

	def sendAccept(self, data) :
		data['type'] = "accept"
		self.leaderNetwork.send(data)

	def sendAck(self, data) :
		data['type'] = "ack"
		self.leaderNetwork.send(data, [-1])

	def sendCommit(self, data) :
		data['type'] = "commit"
		self.leaderNetwork.send(data)
		self.events[data['proposal']['slot']] = data['proposal']['event']

	def draftProposal(self, data) :
		self.curProposal = data['proposal']
		self.sendPrepare(data)

	def fillSlot(self, data) :
		self.events[data['proposal']['slot']] = data['proposal']['event']
		self.sendPrepare(data['proposal'] )

	def receivePrepare(self, data) :
		if (self.events[data['proposal']['slot']] != None ) or checkConflict(data['proposal']['event'] ) :
			data['proposal']['event'] = self.events[data['proposal']['slot']]

		if (data['proposalNum'] > self.maxProposalNum ) :
			self.maxProposalNum = data['proposalNum']
			self.sendPromise(data, [-1])
		else :
			data['proposalNum'] = self.maxProposalNum
			data['type'] = "startOver"
			self.leaderNetwork.send(data, [-1])

	def receivePromise(self, data) :
		majority = len(self.leaderNetwork.peer) / 2 + 1
		self.promises.append(data)
		count = 0
		goalProposalNum = 0
		goalPromise = None

		for promise in self.promises:
			count += 1
			if (promise['proposalNum'] > curProposalNum )
				curProposalNum = promise['proposalNum']
				goalPromise = promise

		if (count >= majority ) :
			self.sendAccept(promise)
		
	def checkConflict(other) :
		for event in self.events :
			if (event['day'] != other['day']):
				return False
			if (event['start'] >= other['end']):
				return False
			if (event['end'] <= other['start']):
				return False
			return True


	def receiveAccept(self, data) :
		if (data['proposalNum'] >= self.proposalNum)  :
			self.events[data['proposal']['slot']] = data['proposal']['event']
			self.sendAck(data, [-1])

	def receiveAck(self, data) :
		self.sendCommit(data)

	def receiveCommit(self, data) :
		pass

	def udpReceive(self, node, data) :
		"""save status"""
		self.save()

		print "--------------"
		print data

		if not data['type'] :
			print "message received in UDP does not conform to expected protocal"
			return
		elif data['type'] == "prepare" :
			self.receivePrepare(data)
		elif data['type'] == "" :
			self.receivePromise(data)
		elif data['type'] == "accept" :
			self.receiveAccept(data)
		elif data['type'] == "ack" :
			self.receiveAck(data)
		elif data['type'] == "commit" :
			self.receiveCommit(data)
		elif data['type'] == "propose" :
			self.draftProposal(data)
		elif data['type'] == "fill" :
			self.fillSlot(data)
		elif data['type'] == "startOver" : 
			self.sendPrepare(data)

		"""save status"""
		self.save()
		return

	def nextSlot() :
		i = 0
		while (self.events[i] != None ) :
			i++
		return i

	def proposeAppointment(self, event) :
		data = {}
		data['proposal'] = {}
		data['proposal']['slot'] = nextSlot()
		data['proposal']['event'] = event
		data['type'] = "propose"
		self.leaderNetwork.send(data, [-1])
		

	def save(self):
		"""Write the current status to disk"""
		hd = open(self.path, 'wb')
		status = {}
		status['maxProposalNum'] = self.maxProposalNum
		status['proposalNum'] = self.proposalNum
		status['events'] = self.events
		status['slot'] = self.slot

		pickle.dump(status, hd )
		hd.close()