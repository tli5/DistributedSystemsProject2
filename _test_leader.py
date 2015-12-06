#A basic testing program for the leader library

import sys, time

import network
import leader

node = int(sys.argv[1])

network = leader.LeaderNetwork(network.Network('config/local.cfg', node))

def recv(msg, src):
	print(src, msg)
	pass
network.registerReceive(recv)

print('This is node ' + str(node))

while True:
	text = raw_input()
	if not text: break
	elif text == 'l': print('leader: ' + str(network.leader))
	else: network.send(text, [1-network.node, -1])
