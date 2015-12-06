# paxos-new.py
#The new and improved implementation of paxos

class State(object):
	def __init__(self):
		self.maxPrepare = -1
		self.accNum = -1
		self.accVal = None

class Proposal(object):
	def __init__(self, index, num, value):
		self.index = index
		self.num = num
		self.value = value
		#General state
		self.accNum = -1
		self.accVal = None
		self.stateMode = None
		self.stateCount = 0
	
	def mode(self, mode):
		self.stateMode = mode
		self.stateCount = 0

class Paxos(object):
	def __init__(self, network):
		self.network = network
		self.network.registerReceive(self.receive)
		self.majority = (len(self.network.peer)/2)+1
		
		self.log = []
		self.state = {}
		self.proposals = {}
		
		self.num = 0
	
	def propose(self, value):
		self.num += 1
		p = Proposal(len(self.log), self.num*self.network.node, value)
		p.mode('propose')
		self.proposals[p.num] = p
		self.network.send({
			'type': 'prepare',
			'index': p.index,
			'num': p.num
		})
	
	def handlePrepare(self, node, data):
		index = data['index']
		if not index in self.state:
			self.state[index] = State()
		state = self.state[index]
		if data['num'] > state.maxPrepare:
			state.maxPrepare = data['num']
			self.network.send({
				'type': 'promise',
				'num': data['num'],
				'accNum': state.accNum,
				'accVal': state.accVal
			}, [node])
	
	def handlePromise(self, node, data):
		p = self.proposals[data['num']]
		if p.stateMode != 'propose': return
		if data['accNum'] > p.accNum:
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
	
	def handleAck(self, node, data):
		p = self.proposals[data['num']]
		if p.stateMode != 'accept': return
		p.stateCount += 1
		if p.stateCount >= self.majority:
			p.mode('commit')
			self.network.send({
				'type': 'commit',
				'index': p.index,
				'value': p.value
			})
	
	def handleCommit(self, node, data):
		while len(self.log) <= data['index']:
			self.log += [None]
		self.log[data['index']] = data['value']
	
	def receive(self, node, message):
		type = message['type']
		print(type, message)
		if not type:
			print('no type', message)
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
