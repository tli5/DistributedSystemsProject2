# paxos-new.py
#The new and improved implementation of paxos

class State(object):
	def __init__(self):
		self.maxPrepare = 0
		self.accNum = None
		self.accVal = None
class Proposal(object):
	def __init__(self, index, num, value):
		self.index = index
		self.num = num
		self.value = value

class Paxos(object):
	def __init__(self, network):
		self.network = network
		self.network.registerReceive(self.receive)
		
		self.log = []
		self.state = []
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
	
	def handlePrepare(self, data):
		print('prepare', data)
	
	def receive(self, node, message):
		type = message['type']
		if not type:
			print(message)
		elif type == 'prepare':
			self.handlePrepare(message)
		else:
			print('unhandled', message)
