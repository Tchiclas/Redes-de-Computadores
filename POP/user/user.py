
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
GN = 63

def nextWord(sock):
	word = ''
	while 1:
		char = sock.recv(1)
		if((char == ' ' or char =='\n') and word != ''):
			break
		if(not(word == '' and char == ' ')):
			word = word + char
	return word
	
def backup_request(name_dir):
	try:
		cwd = os.getcwd() 
		dir_path = cwd + '/' + name_dir
		os.chdir(dir_path) #open directory
		list_files = os.listdir(dir_path)
		mess = 'BCK '+ name_dir + ' ' + str(len(list_files))
		for file in list_files:
			created = os.stat(file).st_mtime
			size = os.stat(file).st_size
			date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(created))
			element =  ' ' + file + ' ' + date_time + ' ' + str(size)
			mess = mess + element
		mess = mess +'\n'
		os.chdir(cwd) #close directory
		return mess
	except OSError,e:
		print "ERR: OSError in backup request"

#para escolher o que fazer
def parse():
	login_counter = 0
	IPBS = 0
	portBS = 0
	list_str = [""]
	while (list_str[0] != "exit"):
		string = raw_input("choose an option: ")
		list_str = string.split()
		try:
			commandUser = list_str[0]
		except IndexError,e:
			print "ERR: invalid command format\nargs[0] is null"
			return

		if(commandUser== "login"):   # A FUNCIONAR
			if(login_counter > 0):
				print 'You have to logout first.\n'
			else:

				try:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect((HOST	, PORT))
				except socket.error,e:
					return
			
				try:
					username = str(list_str[1])
					password = str(list_str[2])
				except IndexError,e:
					return

				#resposta do CS
				message = "AUT "+username+" "+password+"\n"
				try:
					s.sendall(message)
					data = str(s.recv(16))
					s.close()
				except socket.error,e:
					return
				
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
					print data #format error message from CS
				
		
		elif(commandUser == "deluser"):    # A FUNCIONAR
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))
			except (socket.error,socket.gaierror),e:
				print "ERR: deluser command, socket error\n"
				print e
				return
			try:
				s.sendall("AUT "+username+" "+password+"\n")
				#verificacao do pedido de autenticacao ao CS
				if (s.recv(16) != 'AUR OK\n'):
					print 'ERR' 

				s.sendall("DLU\n")
				data = s.recv(1024)	
			except socket.error,e:
				print "ERR: socket error\n deluser attempt unsuccessful"
				return

			if(data == "DLR OK\n"):
				print "User deleted!"
				login_counter = 0
			else:
				print "ainda ha ficheiros nos BS"
			try:
				s.close()
			except socket.error,e:
				return
		elif(commandUser == "backup"):
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))

				#login
				s.sendall("AUT "+str(username)+" "+str(password)+"\n")
				data = s.recv(16) #AUR OK
				directory = list_str[1]
				s.sendall(backup_request(directory))

				tag = nextWord(s) #BKK
				IPBS = nextWord(s)
				portBS = int(nextWord(s))
				n_files = nextWord(s)
				
				i = 0
				replyBS ='UPL ' + directory + ' ' + n_files
				completedReq = ''
				try:
					cwd = os.getcwd()
				except OSError,e:
					return
				path = cwd + '/'  + directory #+ '/' + list_files[index]
				os.chdir(path) #open directory
				while (i < int(n_files)):
					filename = nextWord(s)
					date = nextWord(s)
					time_ = nextWord(s)
					size = int(nextWord(s))
					f = open(filename,'rb')
					l = f.read(int(size))
					f.close()
					replyBS = replyBS + ' ' + filename + ' ' + str(date) + ' ' + time_ + ' ' + str(size) + ' ' + str(l)
					completedReq = completedReq + ' ' + filename
					i = i + 1

				replyBS = replyBS + '\n'
			
			except (socket.error, socket.gaierror),e:
				print "ERR"
				return
	
			#BKR IPBS portBS N (filename date_time size)*
			
			print 'backup to: ' + str(IPBS) + ' ' + str(portBS)
			try:
				s.close()
			except socket.error,e:
				return

			#request upload BS TCP
			try:
				sockUPL = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sockUPL.connect((IPBS	, portBS))
				sockUPL.sendall("AUT " + str(username) + " " + str(password)+"\n")
				dataAUT = sockUPL.recv(1024) #AUR OK
				
			except (socket.error,socket.gaierror),e:
				return
			if (dataAUT == 'AUR OK\n'):
				try:
					lenght_str = len(replyBS)
					sizeSend = 100
					if (lenght_str < sizeSend):
						sockUPL.sendall(replyBS)
					else:
						while (lenght_str > 0):
							send = replyBS[:sizeSend]
							replyBS = replyBS[sizeSend:]
							sockUPL.sendall(send)
							lenght_str = lenght_str - sizeSend

				except socket.error,e:
					return
				try:
					dataUPL = sockUPL.recv(1024)
					os.chdir(cwd) #close directory
					sockUPL.close()
				except (socket.error,OSError),e:
					return
				if(dataUPL == 'UPR OK\n'):
					message = 'completed - ' + directory + ':'
					print message + completedReq
				
				else:
					print 'upload failed , UPL'
			else:
				print 'upload failed, AUR OK'
			
		elif(commandUser == "restore"):
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))

				#first login
				s.sendall("AUT "+str(username)+" "+str(password)+"\n")
				data = s.recv(16) #AUR OK		
				
				directory = list_str[1]

				s.sendall("RST "+ directory +"\n")
				data = s.recv(1024) #RSR IPBS portBS
				data = data.split()
				if(len(data) == 3):
					IPBS = data[1]
					portBS = data[2]
					#request download BS (TCP)
					sockRST = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sockRST.connect((IPBS	, int(portBS)))
					sockRST.sendall("AUT "+str(username)+" "+str(password)+"\n")
					dataAUT = sockRST.recv(1024) #AUR Ok
					if (dataAUT == 'AUR OK\n'):
						message = 'RSB ' + directory + '\n'
						sockRST.sendall(message)
						dataRST = nextWord(sockRST) #RSR
						i = 0
						n = int(nextWord(sockRST)) #N
						reply = ''
						i = 0
						cwd = os.getcwd()
						dir_path = cwd + '/' + directory
						if(os.path.isdir(dir_path)):
							os.chdir(dir_path) #open directory
						else:
							os.makedirs(dir_path)
							os.chdir(dir_path) #open directory
						while i < n:
							#tenho que ter em conta ficheiros que ja fiz backup nao alterados?
							filename = nextWord(sockRST)
							date = nextWord(sockRST)
							time_ = nextWord(sockRST)
							size = int(nextWord(sockRST))
							i = i + 1
							if (filename in os.listdir(dir_path)):
								f = open(filename, 'wb')
								f.close()
							left_size = size
							f = open(filename, 'ab')
							while(left_size > 0):
								if(left_size < 256 or left_size == 256):
									dataRST= sockRST.recv(left_size) #receive data from file
								else:
									dataRST= sockRST.recv(256) #receive data from file
								f.write(dataRST)
								left_size = left_size - len(dataRST)
							f.close()
						sockRST.close()
						os.chdir(cwd) #close directory
					else:
						print 'Restore failed'

				else:
					print 'Restore failed'

				#print "restore"

				s.close()

			except (socket.error, socket.gaierror),e:
				return

		elif(commandUser == "dirlist"):  
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))

				s.sendall("AUT "+username+" "+password+"\n")
				reply = s.recv(1024)
				if (reply == 'AUR OK\n'):
					s.send("LSD\n")
					tag = nextWord(s)
					print tag
					n_files = nextWord(s)
					print n_files
					i = 0
					while ( i< int(n_files)):
						print nextWord(s)
						i = i + 1
					s.close()
				else:
					print 'AUR NOK\n'
			except (socket.error, socket.gaierror),e:
				return


		elif(commandUser == "filelist"):    #A PARTE DO USER JA ESTA A FUNCIONAR
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))
			
				#primeiro fazer a autentificacao
				s.sendall("AUT "+username+" "+password+"\n")
				if(s.recv(16) != 'AUR OK\n'):
					print 'AUR NOK\n'
				else:	
					directory = list_str[1]
					s.sendall("LSF "+directory+"\n")
					data = s.recv(4096) #LFD IPBS portBS N fileinfo
					if(data == "LFD NOK\n"): #----------------------neste momento se ha um pedido invalido, como listar ficheiros de uma diretoria que nao existe o user printa erro e vai se embora
						print "ERR: No such file"
						return
					data = data.split()
					i = 0
					while ( i < 4 * int(data[3])):
						print i
						print nextWord(s)
						i = i + 1

					s.close()
			except (socket.error, socket.gaierror),e:
				return


		elif(commandUser == "delete"):
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))
				directory = list_str[1]
				#first login
				s.sendall("AUT "+str(username)+" "+str(password)+"\n")
				data = s.recv(16) #AUR OK
				if(data == 'AUR OK\n'):
					s.sendall('DEL ' + directory + '\n') #DEL request to CS
				data = s.recv(16) #DDR OK
				if (data == 'DDR OK\n'):
					print directory + ' deleted'
				else: 
					print directory + 'not deleted'
				s.close()
			except (socket.error, socket.gaierror),e:
				return

		elif(commandUser == "logout"):  # JA ESTA A FUNCIONAR
			print 'User: ' + '\"' + username + '\"' + ' logged out\n'		
			username = ""
			password = ""
			login_counter = 0

		elif(commandUser == "exit"):    # JA ESTA A FUNCIONAR ( SO QUANDO O UTILIZADOR ESTA LOGGED IN ? )
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))
				
				s.send("AUT "+username+" "+password+"\n")
			
				print "exit"
				s.sendall("OUT\n")
			except (socket.error, socket.gaierror),e:
				return
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
		try:
			HOST = socket.gethostbyname(str(sys.argv[2]))
		except socket.herror,e:
			print "ERR: could not get host by name"
		PORT = 58000 + GN
	elif(sys.argv[1] == "-p"):
		PORT = int(sys.argv[2])
		HOST = "localhost"
elif(len(sys.argv) == 5):
	try:
		HOST = socket.gethostbyname(str(sys.argv[2]))
	except socket.herror,e:
			print "ERR: could not get host by name"
	PORT = int(sys.argv[4])
else:
	PORT = 58000 + GN
	HOST = "localhost"



parse()


