# paxos-new.py
#The new and improved implementation of paxos

class State(object):
	def __init__(self):
		self.maxPrepare = 0
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
		self.accCount = 0

class Paxos(object):
	def __init__(self, network):
		self.network = network
		self.network.registerReceive(self.receive)
		
		self.log = {}
		self.state = {}
		self.proposals = {}
		
		self.num = 0
	
	def propose(self, value):
		self.num += 1
		p = Proposal(len(self.log), self.num, value)
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
		if data['accNum'] > p.accNum:
			p.accNum = data['accNum']
			p.accVal = data['accVal']
		p.accCount += 1
		if p.accCount >= len(self.network.peer):
			if p.accNum >= 0:
				p.value = p.accVal
			self.network.send({
				'type': 'accept',
				'index': p.index,
				'num': p.num,
				'value': p.value
			})
	
	def receive(self, node, message):
		type = message['type']
		print(type, message)
		if not type:
			print('no type', message)
		elif type == 'prepare':
			self.handlePrepare(node, message)
		elif type == 'promise':
			self.handlePromise(node, message)
		else:
			print('unhandled', message)
