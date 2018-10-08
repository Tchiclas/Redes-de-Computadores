


'''
everything related to the user 

atencao!! nao estou a fazer nenhuma verificao de erros!

'''

#primeiro tenho de fazer o login, logo comeco por fazer a funcao que conecta os 2

import sys
import socket
import os
import datetime
import time


global HOST
global PORT
global username
global password
global new
GN = 77





def backup_request(name_dir):

	cwd = os.getcwd()
	dir_path = cwd + '/' + name_dir
	os.chdir(dir_path)
	list_files = os.listdir(dir_path)
	mess = 'BCK '+ name_dir + ' ' + str(len(list_files))
	for file in list_files:
			created = os.stat(file).st_mtime
			size = os.stat(file).st_size
			date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(created))
			element =  ' ' + file + ' ' + date_time + ' ' + str(size)
			mess = mess + element
			mess = mess +'\n'
	os.chdir(cwd)
	return mess

#para escolher o que fazer
def parse():
	login_counter = 0
	IPBS = 0
	portBS = 0
	list_str = [""]
	while (list_str[0] != "exit"):


		string = raw_input("choose an option: ")
		list_str = string.split()
		

		if(list_str[0] == "login"):   # A FUNCIONAR
			if(login_counter > 0):
				print 'You have to logout first.\n'
			else:
				#global login_counter
				

				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))
			

				username = str(list_str[1])
				password = str(list_str[2])

				#resposta do CS
				message = "AUT "+username+" "+password+"\n"
				s.sendall(message)
				data = str(s.recv(16))
				s.close()
				#print data
				if (data == "AUR NEW\n"):
					login_counter = login_counter + 1
					new = True
					print 'User: ' + '\"' + username + '\"' + ' created\n'
				elif(data == "AUR OK\n"):
					login_counter = login_counter + 1
					new = False
					print 'User: ' + '\"' + username + '\"' + ' logged in\n'
				else:
					new = False
					print 'Erro\n'
				#s.close()
		
		elif(list_str[0] == "deluser"):    # A FUNCIONAR

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))
		

			s.sendall("AUT "+username+" "+password+"\n")
			#verificacao do pedido de autenticacao ao CS
			if (s.recv(16) != 'AUR OK\n'):
				print 'ERR' 

			s.sendall("DLU\n")
			data = s.recv(1024)	

			if(data == "DLR OK\n"):
				print "User deleted!"
				login_counter = 0
			else:
				print "ainda ha ficheiros nos BS"

			s.close()

		elif(list_str[0] == "backup"):

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))

			#login
			s.sendall("AUT "+str(username)+" "+str(password)+"\n")
			data = s.recv(16) #AUR OK
			directory = list_str[1]
			s.sendall(backup_request(directory))

			data = s.recv(4098)

			print data
	
			#BKR IPBS portBS N (filename date_time size)*
			replyCS = data.split()
			IPBS = replyCS[1]
			portBS = int(replyCS[2])
			n_files = replyCS[3]
			list_files = replyCS[4:]
			index = 0
			length = len(list_files)
			cwd = os.getcwd()
			print 'backup to: ' + str(IPBS) + ' ' + str(portBS)


			#request upload BS TCP
			sockUPL = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockUPL.connect((IPBS	, portBS))
			sockUPL.sendall("AUT "+str(username)+" "+str(password)+"\n")
			#sockUPL.sendall(message)
			message = 'UPL ' + directory + ' ' + n_files
			sockUPL.sendall(message)
			while index < length:
				path = cwd + '/' + directory + '/' + list_files[index]
				size = list_files[index+3]
				send = ' ' + ' '.join(list_files[index:index+4]) + ' '
				sockUPL.send(send)
				file = open(path,'rb')
				l = file.read(int(size))
				sockUPL.send(l)
				file.close()
				index = index + 4
			sockUPL.send('\n')
			dataUPL = sockUPL.recv(1024)
			sockUPL.close()
			if(dataUPL == 'UPR OK\n'):
				message = 'completed - ' + directory + ':'
				index = 0
				while (index < length):
					message = message + ' ' + list_files[index]
					index = index + 4
				print message
			else:
				print 'upload failed'
			
			s.close()
		
		elif(list_str[0] == "restore"):

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))

			#first login
			s.sendall("AUT "+str(username)+" "+str(password)+"\n")
			data = s.recv(16) #AUR OK		
			
			s.sendall("RST "+list_str[1]+"\n")

			print "restore"

			s.close()

		elif(list_str[0] == "dirlist"):  # A PARTE DO USER JA ESTA A FUNCIONAR

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))

			s.sendall("AUT "+username+" "+password+"\n")
			print  s.recv(1024)

			s.send("LSD\n")
			print s.recv(5120)
			s.close()

		elif(list_str[0] == "filelist"):    #A PARTE DO USER JA ESTA A FUNCIONAR

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))
		
			#primeiro fazer a autentificacao
			s.sendall("AUT "+username+" "+password+"\n")
			print  s.recv(16)

			s.sendall("LSF "+list_str[1]+"\n")
			data = s.recv(4096) 
			print data #por agora esta assim pq nao sei qual e o formato que se quer apresentar
			s.close()

		elif(list_str[0] == "delete"):

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))

			#first login
			s.sendall("AUT "+str(username)+" "+str(password)+"\n")
			data = s.recv(16) #AUR OK
			s.close()

			print "delete"
		elif(list_str[0] == "logout"):  # JA ESTA A FUNCIONAR
			print 'User: ' + '\"' + username + '\"' + ' logged out\n'		


			#faz com que seja preciso fazer login outra vez
			#global login_counter
			username = ""
			password = ""
			login_counter = 0

		elif(list_str[0] == "exit"):    # JA ESTA A FUNCIONAR ( SO QUANDO O UTILIZADOR ESTA LOGGED IN ? )
		
			print "exit"
			break;
		else:
			print "Invalid option!"

		replyCS = ['nao sei']
		if (replyCS[0] == 'BKR'):
			print 'BKR OK'

		


#HOST = socket.gethostbyname(str(sys.argv[2]))
#PORT = int(sys.argv[4])

if(len(sys.argv) == 3):
	if(sys.argv[1] == "-n"):
		HOST = socket.gethostbyname(str(sys.argv[2]))
		PORT = 58000 + GN
	elif(sys.argv[1] == "-p"):
		PORT = int(sys.argv[2])
		HOST = "localhost"
elif(len(sys.argv) == 5):
	HOST = socket.gethostbyname(str(sys.argv[2]))
	PORT = int(sys.argv[4])
else:
	PORT = 58000 + GN
	HOST = "localhost"

#print len(sys.argv)
#print HOST
#print PORT


#print backup_request("RC")

parse()

#print "CSname: "+ sys.argv[1] + " CSport: "+str(int(sys.argv[2])+1)


