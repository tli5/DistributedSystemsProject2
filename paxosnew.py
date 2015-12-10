# paxos-new.py
#The new and improved implementation of paxos

import threading
from pprint import pformat

class State(object):
	def __init__(self, data = None):
		self.maxPrepare = -1
		self.accNum = -1
		self.accVal = None
		
		#Load from '__dict__'
		if data != None:
			self.maxPrepare = data['maxPrepare']
			self.accNum = data['accNum']
			self.accVal = data['accVal']

class Proposal(object):
	def __init__(self, index, num, value):
		self.index = index
		self.num = num
		self.value = value
		self.valueOriginal = value
		#General state
		self.accNum = -1
		self.accVal = None
		self.stateMode = None
		self.stateCount = 0
		#Timeout
		self.timeout = None
		self.failFunc = None
	
	def __del__(self):
		if self.timeout:
			self.timeout.cancel()
	
	def fail(self):
		self.mode('failed')
		self.timeout.cancel()
		self.failFunc(self)
	
	def mode(self, mode):
		self.stateMode = mode
		self.stateCount = 0
		if self.timeout: self.timeout.cancel()
		self.timeout = threading.Timer(1, self.fail)
		self.timeout.start()

class Paxos(object):
	def __init__(self, network):
		self.network = network
		self.network.registerReceive(self.receive)
		self.network.onBecomeLeader = self.becomeLeader
		self.majority = (len(self.network.peer)/2)+1
		
		#Events
		self.onCommit = None
		self.onFail = None
		
		#Internal state
		self.log = []
		self.state = {}
		self.proposals = {}
		
		#Local proposal number/queue
		#When you request a proposal, it goes here
		#When we get a number form the leader it is actually proposed
		self.proposalQueue = []
		self.num = 0
		
		#Save/load
		self.path = ('data' + str(self.network.node) + '.sav')
		self.load()
	
	def __del__(self):
		for p in self.proposalQueue:
			p.timeout.cancel()
		for p in self.proposals.values():
			p.timeout.cancel()
		self.network.exit = True
		self.network.network.exit = True
	
	def retrieveLog(self):
		return [ev for ev in self.log if ev != None]
	
	def proposeFail(self, p):
		if p.num in self.proposals:
			if self.onFail:
				self.onFail(p.valueOriginal, p.index)
			del self.proposals[p.num]
		elif p in self.proposalQueue:
			if self.onFail:
				self.onFail(p.valueOriginal, p.index)
			self.proposalQueue.remove(p)
	
	def propose(self, value):
		self.num += 1
		index = len(self.log)
		if None in self.log: index = self.log.index(None)
		p = Proposal(index, self.num, value)
		p.failFunc = self.proposeFail
		p.mode('queue')
		self.proposalQueue.insert(0, p)
		self.network.send({'type': 'numreq'}, [-1])
		
	def handleNumReq(self, node, data):
		self.num += 1
		self.network.send({
			'type': 'numset',
			'num': self.num
		}, [node])
		self.save()
	
	def handleNumSet(self, node, data):
		self.num = max(data['num'], self.num)
		if len(self.proposalQueue) > 0:
			p = self.proposalQueue.pop()
			p.num = data['num']
			p.mode('propose')
			self.proposals[p.num] = p
			self.network.send({
				'type': 'prepare',
				'index': p.index,
				'num': p.num
			})
		self.save()
	
	def handlePrepare(self, node, data):
		index = data['index']
		if not index in self.state:
			self.state[index] = State()
		state = self.state[index]
		if data['num'] > state.maxPrepare:
			state.maxPrepare = data['num']
			if index < len(self.log):
				if self.log[index] != None and state.accVal == None:
					state.accVal = self.log[index]
			self.network.send({
				'type': 'promise',
				'num': data['num'],
				'accNum': state.accNum,
				'accVal': state.accVal
			}, [node])
		self.save()
	
	def handlePromise(self, node, data):
		if not data['num'] in self.proposals: return
		p = self.proposals[data['num']]
		if p.stateMode != 'propose': return
		if data['accNum'] >= p.accNum:
			p.accNum = data['accNum']
			p.accVal = data['accVal']
		p.stateCount += 1
		if p.stateCount >= self.majority:
			p.mode('accept')
			if p.accNum >= 0:
				p.value = p.accVal
			self.network.send({
				'type': 'accept',
				'index': p.index,
				'num': p.num,
				'val': p.value
			})
	
	def handleAccept(self, node, data):
		index = data['index']
		if not index in self.state:
			self.state[index] = State()
		state = self.state[index]
		if data['num'] >= state.maxPrepare:
			state.accNum = data['num']
			state.accVal = data['val']
			self.network.send({
				'type': 'ack',
				'index': index,
				'num': state.accNum,
				'val': state.accVal
			}, [node])
		self.save()
	
	def handleAck(self, node, data):
		if not data['num'] in self.proposals: return
		p = self.proposals[data['num']]
		if p.stateMode != 'accept': return
		p.stateCount += 1
		if p.stateCount >= self.majority:
			p.mode('commit')
			self.network.send({
				'type': 'commit',
				'index': p.index,
				'value': p.value,
				'num': p.num
			})
	
	def handleCommit(self, node, data):
		index = data['index']
		while len(self.log) <= index:
			self.log += [None]
		self.log[index] = data['value']
		if self.onCommit:
			self.onCommit(self.log[index], index)
		if node == self.network.node:
			p = self.proposals[data['num']]
			if p.value != p.valueOriginal:
				p.fail()
			if p.num in self.proposals:
				del self.proposals[p.num]
		self.save()
	
	def receive(self, node, message):
		type = message['type']
		if not type:
			print('no type', message)
		elif type == 'numreq':
			self.handleNumReq(node, message)
		elif type == 'numset':
			self.handleNumSet(node, message)
		elif type == 'prepare':
			self.handlePrepare(node, message)
		elif type == 'promise':
			self.handlePromise(node, message)
		elif type == 'accept':
			self.handleAccept(node, message)
		elif type == 'ack':
			self.handleAck(node, message)
		elif type == 'commit':
			self.handleCommit(node, message)
		else:
			print('unhandled', message)
	
	def becomeLeader(self):
		self.network.send({'type': 'numreq'})
	
	def load(self):
		try:
			f = open(self.path, 'r')
			data = f.read().split('\n\n')
			f.close()
			self.num = eval(data[0])
			self.log = eval(data[1])
			stateData = eval(data[2])
			self.state = {k: State(v) for k, v in stateData.iteritems()}
		except Exception as e:
			print(e)
			self.state = {}
			self.log = []
	
	def save(self):
		f = open(self.path, 'w')
		f.write(pformat(self.num))
		f.write('\n\n')
		f.write(pformat(self.log))
		f.write('\n\n')
		stateData = {k: v.__dict__ for k, v in self.state.iteritems()}
		f.write(pformat(stateData))
		f.write('\n')
		f.close()
