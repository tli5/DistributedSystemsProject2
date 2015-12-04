#A basic testing program for the leader library

import sys, time

import network
import leader

node = int(sys.argv[1])

netInternal = network.Network('config/local.cfg', node)
network = leader.LeaderNetwork(netInternal)

def recv(msg, src):
	#print(src, msg)
	pass
network.registerReceive(recv)

print('This is node ' + str(node))

while True:
	network.send('Hello from node ' + str(node), [-1])
	time.sleep(15)
