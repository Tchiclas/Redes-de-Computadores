'''
everything related to the central server 

'''


import socket
import sys

HOST = 'localhost'

#o valor generico sera 58000 mais o numero do grupo
GN = 0  #GN sera o numero do grupo

#------chamar no inicio
def parse():

	#definir o PORT
	if(len(sys.argv) != 1):
		PORT = sys.argv[1]
	PORT = 58000 +GN

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('localhost', PORT))
	s.listen(1)
	conn, addr = s.accept()

	while 1:
	    data = conn.recv(3)
	    if(data == "AUT"):

	    	username = conn.recv(16)
	    	password = conn.recv(16)

	    	print str(username) #imprime o username
	    	print str(password) #imprime a password

	    	#if(len(username) != 5 || len(password) != 8):
	    	#	conn.sendall("AUR NOK")

	    	#falta verificar o utilizador
	    	conn.sendall("AUR OK")

	    elif(data == "DLU"):
	    	print "DLU"
	    elif(data == "BCK"):
	    	print "BCK"
	    elif(data=="RST"):
	    	print "RST"
	    elif(data == "LSD"):
	    	print "LSD"
	    elif(data == "LSF"):
	    	print "LSF"
	    elif(data == "DEL"):
	    	print "DEL"
	    elif(data == "OUT"):
	    	print "OUT"
	    	break;
	    else:
	    	print "ERR"
	    	s.close()
	    print 'Received', repr(data)
	    #conn.sendall(data)

	s.close()

parse()