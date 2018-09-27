'''
everything related to the backup server 
'''


import socket
import sys

#o valor generico do PORT sera 59000

BSPORT = 59000
CSPORT = 58063
CSNAME = ''

def create_backup_server():
	l=len(sys.argv)
	for x in sys.argv:
		if x == '-b':
			BSPORT=sys.argv[3]
		if x == '-n':
			CSNAME=sys.argv[5]
		if x == '-p':
			CSPORT=sys.argv[1] 

def handlerRGR(status):
	if(not status == 'OK'):
		print 'Deu barraca'

def parse():

	create_backup_server()
	# Create a UDP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (CSNAME, CSPORT)
	message = 'REG ' + str(BSPORT) + CSNAME
	sock.sendto(message, server_address)

	while 1:
		data,addr = sock.recvfrom(1024)
		#data.split()
		if(data == "RGR OK"):
			print 'Recebi!'
			handlerRGR(data[1])
		elif(data[0] == "UAR"):
			if(not data[1] == 'OK'):
				print 'UAR ERR'
		elif(data[0] == "LSF"):
			user = data[1]
			dir = data[2]
			handlerLSF(user, dir)
		elif(data[0] == "LSU"):
			user = data[1]
			passw = data[2]
			registerUser(user,passw)
		elif(data[0] == "DLB"):
			user = data[1]
			dir = data[2]
			handlerDLB(user,dir)
        else:
			print "ERR"
			sock.close()

parse()