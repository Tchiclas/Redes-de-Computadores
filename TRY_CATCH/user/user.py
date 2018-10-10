
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
GN = 79


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
				#global login_counter
				
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
				print "ERR: deluser command, socket error\n" + e
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

				data = s.recv(4098) #BKR IPBS portBS N (filename date_time size)*
			except (socket.error, socket.gaierror),e:
				print "ERR"
				return
	
			#BKR IPBS portBS N (filename date_time size)*
			try:
				replyCS = data.split()
				IPBS = replyCS[1]
				portBS = int(replyCS[2])
				n_files = replyCS[3]
				list_files = replyCS[4:]
				index = 0
				length = len(list_files)
			except IndexError,e:
				print "ERR: " + e
				return
			try:
				cwd = os.getcwd()
			except OSError,e:
				return
			print 'backup to: ' + str(IPBS) + ' ' + str(portBS)
			try:
				s.close()
			except socket.error,e:
				return

			#request upload BS TCP
			try:
				sockUPL = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sockUPL.connect((IPBS	, portBS))
				sockUPL.sendall("AUT "+str(username)+" "+str(password)+"\n")
				dataAUT = sockUPL.recv(1024) #AUR Ok
			except (socket.error,socket.gaierror),e:
				return
			if (dataAUT == 'AUR OK\n'):
				#sockUPL.sendall(message)
				message = 'UPL ' + directory + ' ' + n_files
				try:
					sockUPL.sendall(message)
				except socket.error,e:
					return
				try:
					while index < length:
						path = cwd + '/'  + directory #+ '/' + list_files[index]
						filename = list_files[index]
						os.chdir(path) #open directory
						print 'list_files[index] : ' + str(list_files[index])
						size = list_files[index+3]
						send = ' ' + ' '.join(list_files[index:index+4]) + ' '
						sockUPL.send(send)
						file = open(filename,'rb')
						l = file.read(int(size))
						sockUPL.send(l)
						file.close()
						index = index + 4
				except (IOError, OSError),e:
					print "ERR: backup operation had a problem handling directories"
					return
				try:
					sockUPL.send('\n')
					dataUPL = sockUPL.recv(1024)
					os.chdir(cwd) #close directory
					sockUPL.close()
				except (socket.error,OSError),e:
					return
				if(dataUPL == 'UPR OK'):
					
					message = 'completed - ' + directory + ':'
					index = 0
					while (index < length):
						message = message + ' ' + list_files[index]
						index = index + 4
					print message
				else:
					print 'upload failed'
			else:
				print 'upload failed'
			
			
		
		elif(commandUser == "restore"):
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))

				#first login
				s.sendall("AUT "+str(username)+" "+str(password)+"\n")
				data = s.recv(16) #AUR OK		
				
				s.sendall("RST "+list_str[1]+"\n")

				print "restore"

				s.close()
			except (socket.error, socket.gaierror),e:
				return

		elif(commandUser == "dirlist"):  
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))

				s.sendall("AUT "+username+" "+password+"\n")
				print  s.recv(1024)


				s.send("LSD\n")
				tag = s.recv(5120)
				print tag
				tag = tag.split()
				i = 0
				while ( i< int(tag[1])):
					print s.recv(1024)
					i = i + 1

				s.close()
			except (socket.error, socket.gaierror),e:
				return


		elif(commandUser == "filelist"):    #A PARTE DO USER JA ESTA A FUNCIONAR
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((HOST	, PORT))
			
				#primeiro fazer a autentificacao
				s.sendall("AUT "+username+" "+password+"\n")
				
				
				print  s.recv(16)  
				"""#
				
				
				
				falta verificacao se autenticacao correu OK 
				
				
				
				"""
				directory = list_str[1]
				s.sendall("LSF "+directory+"\n")
				data = s.recv(4096) #LFD IPBS portBS N fileinfo
				if(data == "LFD NOK\n"): #----------------------neste momento se ha um pedido invalido, como listar ficheiros de uma diretoria que nao existe o user printa erro e vai se embora
					print "ERR"
					return
				data = data.split()
				i = 0
				while ( i < 4 * int(data[3])):
					print s.recv(1024)
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
					s.sendall('DEL ' + directory) #DEL request to CS
				data = s.recv(16) #DDR OK
				if (data == 'DDR OK\n'):
					print directory + ' deleted'
				else: 
					print directory + 'not deleted'
				s.close()
			except (socket.error, socket.gaierror),e:
				return

		elif(commandUser == "logout"):  # JA ESTA A FUNCIONAR
		
			#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#s.connect((HOST	, PORT))
			
			#s.send("AUT "+username+" "+password+"\n")
			print 'User: ' + '\"' + username + '\"' + ' logged out\n'		
			#s.sendall("OUT\n")

			#faz com que seja preciso fazer login outra vez
			#global login_counter
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


