"""
everything related to the backup server 
63
"""
import socket
import sys

#numero do grupo
GN = 94

BSPORT = 59000 #usar na comunicacao BS - user
CSPORT = 58000 + GN #usar na comunicacao BS - CS
CSNAME = ""

#dictionary with username as keyword
users = {"12345":"aaaaaaaa"}

def register_user(username,password):
	users[str(username)] = str(password)

#handles flag values
def create_backup_server():
	l=len(sys.argv)
	global BSPORT
	global CSNAME
	global CSPORT
	i = 1
	while i < l:  
		if sys.argv[i] == '-b':
			BSPORT = int(sys.argv[i+1])
		if sys.argv[i] == '-n':
			CSNAME = sys.argv[i+1]
		if sys.argv[i] == '-p':
			CSPORT = int(sys.argv[i+1])
		i = i + 2
#atencao tem de se acrescentar o \n no final do ok!!!!!
def handlerRGR(status):
	if( status != 'OK'):
		print 'ERR'   #QUAL E A MENSAGEM DE REGISTO NAO POSSIVEL? - CONFIRMAR
	

def parse():

	create_backup_server()
	# Create a UDP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (CSNAME, CSPORT)
	message = 'REG ' + str(BSPORT) + CSNAME
	sock.sendto(message, server_address)

	while 1:
		
		data,addr = sock.recvfrom(1024)
		print data
		command = data.split()
		if(command[0] == "RGR"):
			handlerRGR(command[1])
		elif(command[0] == "UAR"):
			if(not command[1] == 'OK'):
				print 'UAR ERR'
		elif(command[0] == "LSF"):
			user = command[1]
			dir = command[2]
			handlerLSF(user, dir)
		elif(command[0] == "LSU"):
			user = str(command[1])
			passw = str(command[2])
			register_user(user,passw)
			print 'New user: ' + user
			sock.sendto('LUR OK', server_address)
		elif(command[0] == "DLB"):
			user = command[1]
			dir = command[2]
			handlerDLB(user,dir)
        else:
			print "ERR"
			sock.close()

parse()