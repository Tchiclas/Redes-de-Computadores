"""
everything related to the backup server 

"""
import socket
import sys
import os
import time

#numero do grupo
GN = 77

BSPORT = 59000 #usar na comunicacao BS - user
CSPORT = 58000 + GN #usar na comunicacao BS - CS
CSNAME = ""
BSNAME = socket.gethostname()

#dictionary with username as keyword
users = {"12345":"aaaaaaaa"}

#data structure with directories with files

def register_user(username,password):
	user_file = 'user_' + username + '.txt'
	file = open(user_file, 'w')
	file.write(password)
	file.close()
	cwd = os.getcwd()
	user_dir = 'user_' + username
	user_dir_path = cwd + '/' + user_dir
	os.makedirs(user_dir_path)

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

def handlerLSF(user, directory, server_address): #NOT DONE!!!!!!
	cwd = os.getcwd() #path of current working directory
	cwd = cwd + '/' + directory
	if(os.path.exists(cwd)):
		os.chdir(cwd) #open directory
		cwd = os.getcwd()
		list_files = os.listdir(cwd)
		nFiles = len(list_files)
		element = 'LFD ' + str(nFiles)  #reply
		connUser.sendall(element)
		for file in list_files:
			created= os.stat(file).st_mtime
			size = os.stat(file).st_size
			date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(created))
			element =  ' ' + file + ' ' + date_time + ' ' + str(size)
			connUser.sendall(element) #file details
		connUSer.sendall('\n')

def parseTCP():
	current_user = ''
	current_pass = ''
	# Create a TCP socket (user)
	sockUser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockUser.bind((BSNAME, BSPORT))
	sockUser.listen(1)
	connUser, addrUser = sockUser.accept()
	print 'accept ' + str(connUser) + ' ' + str(addrUser)
	missingCommand = False
	dataUser = ''

	while 1:
		#messages from users
		if (missingCommand):
			dataUser = commandSplit
			commandSplit = ''
			missingCommand = False
		else:
			dataUser = ''
		dataUser = dataUser + connUser.recv(20)
		requestUser = dataUser.split()
		print requestUser
		if (requestUser[0] == 'AUT'):
			if( len(requestUser) != 3):
				commandSplit = ' '.join(requestUser[3:])
				missingCommand = True
			us = str(requestUser[1])
			pa = str(requestUser[2])
			user_file = 'user_' + us + '.txt'
			file = open(user_file, 'r')
			password = file.read()
			if(pa == password):
				connUser.sendall("AUR OK")
				current_user = us
				current_pass = pa
				print 'User: '+str(current_user)
			else:
				connUser.sendall("AUR NOK")

		elif (requestUser[0] == 'UPL'):
			dir_name = requestUser[1]
			num_files = requestUser[2]
			cwd = os.getcwd()
			user_dir = 'user_' + current_user
			user_dir_path = cwd + '/' + user_dir
			dir_path = user_dir_path + '/' + dir_name
			if (not dir_name in os.listdir(user_dir_path)):
				os.makedirs(dir_path)
			restUPL = ''
			if(len(requestUser) != 3):
				index = dataUser.find(requestUser[3])
				restUPL = dataUser[index:]
			dataUPL = restUPL + connUser.recv(44) #filename date time size
			string = dataUPL.split()
			print string
			os.chdir(dir_path) #open directory
			rest_size = 0 
			rest = ''
			while (1):
				filename = string[0]
				size = int(string[3]) - rest_size
				f = open(filename, 'a') #append so I can write data more than once
				dataUPL = connUser.recv(size) #receive data from file
				print dir_name + ': ' + filename + ' ' + string[3] + ' Bytes received'
				f.write(rest)
				f.write(dataUPL)
				dataUPL = connUser.recv(44) #next file details
				string = dataUPL.split()
				print 'string: ' + str(string)
				if (len(string) == 0): #no more files to receive
					break
				if (len(string) > 4): #restore of data of the next file has started
					index = dataUPL.find ( string[4] )
					rest = dataUPL[index:]
					print 'rest: ' + rest
					rest_size = len(rest.encode('utf-8'))
				else:
					rest = ''
					rest_size = 0
			connUser.sendall('UPR OK')
			os.chdir(cwd) #close directory
			#UPL NOK?
			
			""" l = len(requestUser)
			i = 3
			j = 3
			bk = ''
			backup = ''
			while j < l:
				#str stores message to print in BS (file name and num bytes received)
				if (j % 3 == 0):
					bk = bk + str(requestUser[i]) + requestUser[i+3] + 'Bytes received\n'
					i = i + 4
				#stores file to backup in file
				backup = backup + requestUser[j]
				j = j + 1
			print 'RC: ' + bk
			connUser.sendall('UPR OK') """
		elif (requestUser[0] == 'RSB'):
			if (not len(requestUser) == 2):
				connUser.sendall('RBR ERR')
			else:
				directory = requestUser[1]
				cwd = os.getcwd() #path of current working directory
				cwd = cwd + '/' + directory
				if(not os.path.exists(cwd)):
					connUser.sendall('RBR EOF')
				else:
					os.chdir(cwd) #open directory
					cwd = os.getcwd()
					list_files = os.listdir(cwd)
					nFiles = len(list_files)
					element = 'RBR ' + str(nFiles) + ' ' #reply
					connUser.sendall(element)
					for file in list_files:
						created= os.stat(file).st_mtime
						size = os.stat(file).st_size
						date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(created))
						element = file + ' ' + date_time + ' ' + str(size) + ' '
						connUser.sendall(element) #file details
						f = open(file,'rb')
						l = f.read(size)
						connUser.send(l)
						f.close()
        else:
			print "ERR"
			sock.close()
			sockUser.close()

def parseUDP():
	#create_backup_server()
	# Create a UDP socket (CS)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (BSNAME, CSPORT)
	message = 'REG ' + str(BSPORT) + ' ' + BSNAME
	print 'vou enviar msg'
	sock.sendto(message, server_address)
	print 'enviadacom sucesso'
	sock.close()
	#messages from CS
	sockBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (BSNAME, BSPORT)
	sockBS.bind(server_address)
	

	while 1:
		
		data, addr = sockBS.recvfrom(1024)
		print 'received'
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
			handlerLSF(user, dir, addr)
		elif(command[0] == "LSU"):
			if (len(command)== 3):
				user = str(command[1])
				passw = str(command[2])
				print 'aqui '
				register_user(user,passw)
				print 'New user: ' + user
				sockBS.sendto('LUR OK\n', addr)
				print 'sended to: ' + str(addr)
				#sockBS.close()
			else:
				sockBS.sendto('LUR ERR', addr)
		elif(command[0] == "DLB"):
			user = command[1]
			dir = command[2]
			handlerDLB(user,dir)
		#Devia existir algum else aqui?

		
create_backup_server()
pid = os.fork()
if(pid == 0):
	while(1):
		parseTCP() # o filho vai tratar de responder a todos os pedidos TCP
else:
	parseUDP()	# o pai vai tratar de responder a todos os pedidos UDP