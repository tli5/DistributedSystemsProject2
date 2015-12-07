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
		#self.calendar = cal
		self.path = ('paxos' + str(self.node) + '.sav')

		"""load backup if exists"""
		try:
		    hd = open(self.path, "rb")
		    status = pickle.load(hd)

		    if ((status != None) and (status['maxPrepareNum'] != None) ) :
		    	self.maxPrepareNum = status['maxPrepareNum']
		    	self.prepareNum = status['prepareNum']
		    	self.accNum = status['accNum']
		    	self.accVal = status['accVal']
		    	self.events = status['events']
		    	self.slot = status['slot']

		    else :
		    	self.maxPrepareNum = self.prepareNum = 0
		    	self.accNum = self.accVal = None
		    	self.events = []
		    	for i in range (0, 20)
		    		self.events.append(None)
		    	self.slot = 0

		except IOError:
		    self.maxPrepareNum = self.prepareNum = 0
		    self.accNum = self.accVal = None
		    self.events = []
		    self.slot = 0

		
	"""I probably should have refactored below codes using Enum with each value associated with a function"""
	"""I didn't cause there's not much time left to do the research on syntax issues"""
	def sendPrepare(self, data) :
		data['type'] = "prepare"
		self.prepareNum += 1
		"""set response count to 0 every time the proposer tries to propose something"""
		self.promises = []
		self.leaderNetwork.send(data)

	def sendPromise(self, val) :
		data = {}
		data['val'] = val
		data['type'] = "promise"
		self.leaderNetwork.send(data)

	def sendAccept(self, val) :
		data = {}
		data['val'] = val
		data['type'] = "accept"
		self.leaderNetwork.send(data)

	def sendAck(self, val) :
		data = {}
		data['val'] = val
		data['type'] = "ack"
		self.leaderNetwork.send(data)

	def sendCommit(self, val) :
		data = {}
		data['val'] = val
		data['type'] = "commit"
		self.leaderNetwork.send(data)
		self.record(data['val'])

	def draftProposal(self, data) :
		self.proposalVal = data['val']
		self.proposalVal['prepareNum'] = self.prepareNum
		self.sendPrepare(data)

	def fillSlot(self, data) :
		self.events[data['slot']] = data['event']
		self.sendPrepare(data['proposal'] )

	def receivePrepare(self, data) :
		"""send back respective log event if the slot has been filled already"""
		if (self.events[data['val']['slot']] != None ) :
			msg = {}
			msg['type'] = "fill"
			msg['event'] = self.events[data['val']['slot']]
			msg['slot'] = data['val']['slot']
			msg['proposal'] = data
			self.leaderNetwork.send(msg, [data['val']['origin'] ] )
			return

		if (data['prepareNum'] > self.maxPrepareNum ) :
			self.maxPrepareNum = data['prepareNum']
			val = {}
			val['accNum'] = self.accNum
			val['accVal'] = self.accVal
			self.sendPromise(val)
		else :
			msg = {}
			msg['type'] = "lowPrepareNum"
			msg['val'] = self.maxPrepareNum
			
			self.leaderNetwork.send(msg)

	def receivePromise(self, data) :
		majority = len(self.leaderNetwork.peer) / 2 + 1
		self.promises.append(data['val'])

		count = 0
		lgPromise = None

		for promise in self.promises:
			count += 1
			if (promise['accNum'] != None ):
				if (lgPromise is None ) :
					lgPromise = promise
				elif (lgPromise['accNum'] < promise['accNum'] ) :
					lgPromise = promise 

		if (count >= majority ) :
			if (lgPromise != None ):
				val = {}
				val['accNum'] = promise['accNum']
				val['accVal'] = promise['accVal']
				self.sendAccept(val)
			else :
				val = {}
				val['accNum'] = self.prepareNum
				val['accVal'] = self.proposalVal
				self.sendAccept(val)
		

	def receiveAccept(self, data) :
		if (data['prepareNum'] >= self.maxPrepareNum)  :
			self.chosen = {}
			self.chosen['accNum'] = data['val']['accNum']
			self.chosen['accVal'] = data['val']['accVal']
			self.sendAck(self.chosen)


	def receiveAck(self, data) :
		self.sendCommit(data)

	def receiveCommit(self, data) :
		self.record(data['val'] )

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

		elif data['type'] == "lowPrepareNum" :
			"""start over"""
			self.sendPrepare(data)


		"""save status"""
		self.save()
		return

	def proposeAppointment(self, aptInfo) :
		data = {}
		data['val'] = {}
		data['val']['origin'] = self.node
		data['val']['slot'] = self.slot
		data['val']['apt'] = aptInfo['apt']
		data['val']['type'] = aptInfo['type']
		data['type'] = "propose"
		self.leaderNetwork.send(data, [-1])

	def record(self, chosen) :
		if (chosen['accVal']['type'] == "add" ) :
			apt = chosen['accVal']['apt']
			conflict = self.calendar.checkConflicts(apt)
			if (conflict is None ) :
				self.calendar.addAppointment(apt)
		else :
			self.calendar.removeAppointment(chosen['accVal']['index'])
		

	def save(self):
		"""Write the current status to disk"""
		hd = open(self.path, 'wb')
		status = {}
		status['maxPrepareNum'] = self.maxPrepareNum
		status['prepareNum'] = self.prepareNum
		status['accNum'] = self.accNum
		status['accVal'] = self.accVal
		status['slot'] = self.slot
		status['events'] = self.events
		pickle.dump(status, hd )
		hd.close()