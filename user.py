
'''
everything related to the user 

atencao!! nao estou a fazer nenhuma verificao de erros!

'''

#primeiro tenho de fazer o login, logo comeco por fazer a funcao que conecta os 2

import sys
import socket
import os
import datetime


global HOST
global PORT
global username
global password
global new



def backup_request(name_dir):
	#lista de todos os ficheiros dentro da diretoria ".", 
	#mas nao devia ser de qualquer uma ? atraves do name_dir?
	files = [f for f in os.listdir('./'+name_dir) if os.path.isfile(f)]


	mess = 'BCK '+ name_dir+ ' ' + str(len(files))
	dir_files = ''

	for f in files:
		t = os.path.getmtime(f)
		date_specifications = datetime.datetime.fromtimestamp(t)
		size = os.path.getsize(f)
		dir_files = dir_files + ' ' + str(f) + ' ' + str(date_specifications) + ' ' + str(size)

	return mess + dir_files

#para escolher o que fazer
def parse():
	IPBS = 0
	portBS = 0
	list_str = [""]
	while (list_str[0] != "exit"):

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST	, PORT))
		
		string = raw_input("choose an option: ")
		list_str = string.split()
		

		if(list_str[0] == "login"):

			username = str(list_str[1])
			password = str(list_str[2])

			#resposta do CS
			message = "AUT "+username+" "+password+"\n"
			s.sendall(message)
			data = str(s.recv(16))
			if (data == "AUR NEW\n"):
				new = True
				print 'User: ' + '\"' + username + '\"' + ' created'
			elif(data == "AUR OK\n"):
				new = False
				print 'User: ' + '\"' + username + '\"' + ' logged in'
			else:
				new = False
				print 'Erro'
		
		elif(list_str[0] == "deluser"):

			s.sendall("AUT "+username+" "+password+"\n")
			print  s.recv(16)
			s.close()

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))
			s.sendall("DLU\n")
			data = s.recv(1024)	

			if(data == "DLR OK\n"):
				print "User deleted!"
			else:
				print "ainda ha ficheiros nos BS"

		elif(list_str[0] == "backup"):
			#first login
			s.sendall("AUT "+str(username)+" "+str(password)+"\n")
			data = s.recv(16) #AUR OK
			s.close()

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))

			
			s.sendall(backup_request(list_str[1]))
			s.close()

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))
			data = s.recv(4098)

			print data

			#a resposta do CS sera o IP do BS , a porta do BS e 
			replyCS = data.split()
			IPBS = int(replyCS[1])
			portBS = int(replyCS[2])
		
		elif(list_str[0] == "restore"):
			directory = list_str[1]

			#first login with CS
			s.sendall("AUT "+str(username)+" "+str(password)+"\n")
			data = s.recv(16) #AUR OK		
			
			s.sendall("RST "+ directory +"\n")
			data = s.recv(32) #RSR IPBS portBS
			string = data.split()
			IPBS = string[1]
			portBS = string[2]
			s.close()
			
			#User-BS TCP
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((IPBS	, portBS))

			#Autenticacao BS
			s.sendall("AUT "+str(username)+" "+str(password)+"\n")
			data = s.recv(16) #AUR OK	

			s.sendall("RSB "+ directory +"\n")


			string = s.recv(16) #RBR number_of_files
			data = s.recv(44) #filename date time size
			string = data.split()
			cwd = os.getcwd() #path of current working directory
			cwd = cwd + '/' + directory 
			os.makedirs(cwd) #make directory if directory doesn't exist
			os.chdir(cwd) #open directory
			rest_size = 0 
			rest = ''
			while (1):
				filename = string[0]
				size = int(string[3]) - rest_size
				f = open(filename, 'a') #append so I can write data more than once
				data = s.recv(size) #receive data from file
				f.write(rest)
				f.write(data)
				data = s.recv(44) #next file details
				string = data.split()
				print 'string: ' + str(string)
				if (len(string) == 0): #no more files to receive
					break
				if (len(string) > 4): #restore of data of the next file has started
					index = data.find ( string[4] )
					rest = data[index:]
					print 'rest: ' + rest
					rest_size = len(rest.encode('utf-8'))
				else:
					rest = ''
					rest_size = 0
			s.close()


			#print "restore"

		elif(list_str[0] == "dirlist"):

			#primeiro fazer a autentificacao
			if(new):
				s.sendall("AUT "+username+" "+password+"\n")
				print  s.recv(1024)
				s.close()
			
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))

			s.send("LSD\n")
			print s.recv(5120)

		elif(list_str[0] == "filelist"):

			#primeiro fazer a autentificacao
			s.sendall("AUT "+username+" "+password+"\n")
			print  s.recv(16)
			s.close()
			
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))

			s.sendall("LSF "+list_str[1]+"\n")
			data = s.recv(4096) 
			print data #por agora esta assim pq nao sei qual e o formato que se quer apresentar

		elif(list_str[0] == "delete"):

			#first login
			s.sendall("AUT "+str(username)+" "+str(password)+"\n")
			data = s.recv(16) #AUR OK
			s.close()

			print "delete"
		elif(list_str[0] == "logout"):  #NAO E PRECISO FAZER MAIS NADA
			#faz com que seja preciso fazer login outra vez
			username = ""
			password = ""

			print "logout"
		elif(list_str[0] == "exit"):
			print "exit"
			s.sendall("OUT\n")
			break;
		else:
			print "Invalid option!"

		replyCS = ['nao sei']
		if (replyCS[0] == 'BKR'):
			print 'BKR OK'

		
		s.close()


#HOST = socket.gethostbyname(str(sys.argv[2]))
#PORT = int(sys.argv[4])

if(len(sys.argv) == 3):
	if(sys.argv[1] == "-n"):
		HOST = socket.gethostbyname(str(sys.argv[2]))
		PORT = 58063
	elif(sys.argv[1] == "-p"):
		PORT = int(sys.argv[2])
		HOST = "localhost"
elif(len(sys.argv) == 5):
	HOST = socket.gethostbyname(str(sys.argv[2]))
	PORT = int(sys.argv[4])
else:
	PORT = 58063
	HOST = "localhost"

#print len(sys.argv)
#print HOST
#print PORT


#print backup_request("RC")
parse()

#print "CSname: "+ sys.argv[1] + " CSport: "+str(int(sys.argv[2])+1)
