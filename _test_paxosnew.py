#A basic testing program for the paxos library

import sys, time

import paxosnew
import leader
import network

node = int(sys.argv[1])

cal = paxosnew.Paxos(leader.LeaderNetwork(network.Network('config/local.cfg', node)))

print('This is node ' + str(node))

while True:
	text = raw_input()
	if not text: break
	elif text == 'leader': print('leader: ' + str(cal.network.leader))
	elif text == 'log': print('log: ' + str(cal.log))
	else: cal.propose(text)
