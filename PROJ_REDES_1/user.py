
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



def backup_request(name_dir):
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
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
	user = ''
	passw = ''
	while (list_str[0] != "exit"):

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST	, PORT))
		
		string = raw_input("choose an option: ")
		list_str = string.split()
		

		if(list_str[0] == "login"):

			username = str(list_str[1])
			password = str(list_str[2])
			user = username
			passw = password

			#resposta do CS
			message = "AUT "+username+" "+password+"\n"
			s.sendall(message)
			data = str(s.recv(16))
			if (data == "AUR NEW"):
				print 'User: ' + '\"' + username + '\"' + ' created'

		elif(list_str[0] == "deluser"):

			print "deluser"
		elif(list_str[0] == "backup"):
			#first login
			newlogin = "AUT "+str(user)+" "+str(passw)+"\n"
			s.sendall(newlogin)
			data = s.recv(16) #AUR OK

			#nao sei porque mas tenhode fazer isto
			s.close()
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))

			#enviar pedido BCK ao CS
			name_dir = list_str[1]
			askCS = str(backup_request(list_str[1]))
			s.sendall(askCS)
			data = s.recv(4098)  #autorizacao do CS + port e IP do BS
			print data
			replyCS = data.split()
			if (replyCS[1] != 'EOF' and replyCS[1] != 'ERR'):
				IPBS = int(replyCS[1])
				portBS = int(replyCS[2])
				num_files = int (replyCS[3])
				i = 4	
				file_lst = ''
				while i < num_files:
						file_lst = file_lst + str(data[i])
						i = i + 1
				print 'backup to: '+ str(IPBS) + ' ' + str(portBS)
			#connect TCP to BS
			s.close()
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((IPBS	, portBS))

			#first login
			newlogin = "AUT "+str(user)+" "+str(passw)+"\n"
			s.sendall(newlogin)
			data = s.recv(16) #AUR OK

			#close and reopen socket to BS
			s.close()
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((IPBS	, portBS))

			#request backup to BS
			upl_request = 'UPL '+ name_dir + ' ' + num_files + ' ' + file_lst
			s.sendall(upl_request)
			data = s.recv(16) #UPR OK
			#if (data == 'UPR OK'):
			filter_names = file_lst.split()
			i = 0
			l = len(filter_names) 
			while i < l:
				fn = fn + filter_names[i] + ' '
				i = i + 4
			print 'completed - '+ name_dir + ':' + fn

		elif(list_str[0] == "restore"):
			print "restore"
		elif(list_str[0] == "dirlist"):


			s.sendall("AUT "+username+" "+password+"\n")
			print  s.recv(16)
			s.close()
			
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST	, PORT))

			s.sendall("LSD\n")
			print "dirlist"
			print s.recvfrom(1024)

		elif(list_str[0] == "filelist"):
			print "filelist	"
		elif(list_str[0] == "delete"):
			print "delete"
		elif(list_str[0] == "logout"):
			print "logout"
		elif(list_str[0] == "exit"):
			print "exit"
			s.sendall("OUT")
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
elif(len(sys.argv) == 4):
	HOST = socket.gethostbyname(str(sys.argv[2]))
	PORT = int(sys.argv[5])
else:
	PORT = 58099
	HOST = "localhost"





parse()

#print "CSname: "+ sys.argv[1] + " CSport: "+str(int(sys.argv[2])+1)
