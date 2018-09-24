
'''
everything related to the user 

atencao!! nao estou a fazer nenhuma verificao de erros!

'''

#primeiro tenho de fazer o login, logo comeco por fazer a funcao que conecta os 2

import sys
import socket


global host
global port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def login(username,password):

	s.sendall("AUT")
	#envia o user que tem 5 digitos (5 bytes)
	s.sendall(username)
	#envia a pass que tem 8 letras e ou numeros (16 bytes)
	s.sendall(password)

	return s.recv(16)





#para escolher o que fazer 
def parse():
	list_str = [""]
	while (list_str[0] != "exit"):
		string = raw_input("choose an option: ")
		list_str = string.split()
		
		if(list_str[0] == "login"):

			username = str(list_str[1])
			password = str(list_str[2])

			#resposta do CS
			ret = login(username,password)
			print  str(ret)

		elif(list_str[0] == "deluser"):
			print "deluser"
		elif(list_str[0] == "backup"):
			print "backup"
		elif(list_str[0] == "restore"):
			print "restore"
		elif(list_str[0] == "dirlist"):
			print "dirlist"
		elif(list_str[0] == "filelist"):
			print "filelist	"
		elif(list_str[0] == "delete"):
			print "delete"
		elif(list_str[0] == "logout"):
			print "logout"
			s.sendall("OUT")
			break;
		else:
			print "Invalid option!"

host = str(sys.argv[1])
port = int(sys.argv[2])


s.connect((host	, port))

parse()


s.close()
#print "CSname: "+ sys.argv[1] + " CSport: "+str(int(sys.argv[2])+1)