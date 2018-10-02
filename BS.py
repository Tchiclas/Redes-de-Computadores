"""
everything related to the backup server 
63
"""
import socket
import sys
import os

#numero do grupo
GN = 94

BSPORT = 59000 #usar na comunicacao BS - user
CSPORT = 58000 + GN #usar na comunicacao BS - CS
CSNAME = ""

#dictionary with username as keyword
users = {"12345":"aaaaaaaa"}

#data structure with directories with files

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

def handlerLSF(user, dir, server_address):
	#corrigir isto, para parecido com rsb
	filelist = []
	sock.sendto(str(filelist), server_address)


def parse():
	current_user = ''
	current_pass = ''
	create_backup_server()
	# Create a UDP socket (CS)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (CSNAME, CSPORT)
	message = 'REG ' + str(BSPORT) + CSNAME
	sock.sendto(message, server_address)

	# Create a TCP socket (user)
	sockUser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockUser.bind(("", PORT))
	sockUser.listen(1)
	connUser, addrUser = sockUser.accept()

	while 1:
		#messages from CS
		data,addr = sock.recvfrom(1024)
		print data
		command = data.split()

		#messages from users
		dataUser,addrUser = sockUser.recvfrom(1024)
		print dataUser
		requestUser = dataUser.split()

		if(command[0] == "RGR"):
			handlerRGR(command[1])
		elif(command[0] == "UAR"):
			if(not command[1] == 'OK'):
				print 'UAR ERR'
		elif(command[0] == "LSF"):
			user = command[1]
			dir = command[2]
			handlerLSF(user, dir, server_address)
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
		#Devia existir algum else aqui?

		if (requestUser[0] == 'AUT'):
			us = str(requestUser[1])
			pa = str(requestUser[2])
			if(users.has_key(str(username))):
				if(users[str(username)] == str(password)):
					current_user = str(username)
					current_pass = str(password)
					connUser.sendall("AUR OK")
					print 'User: '+str(username)
				else:
					connUser.sendall("AUR NOK")
		elif (requestUser[0] == 'UPL'):
			file_name = requestUser[1]
			num_files = requestUser[2]
			l = len(requestUser)
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
			connUser.sendall('UPR OK')
		elif (requestUser[0] == 'RSB'):
			if (not len(requestUser) == 2):
				connUser.sendall('RBR ERR')
			else:
				directory = requestUser[1]
				cwd = os.getcwd()
				for file in os.listdir(cwd):
        			if file == directory:
            			fileExists = True
            			break
				#ouisto, nao sei bem
				#dir_path = ''
				#file = open('users_directories.txt',"r")
				#for line in file:
    			#	split = line.split()
				#	if(split[1] == directory):
				#		dir_path = directory + '.txt'
				#		break
				#if directory doesn't exist: 
				#if (dir_path == ''):
				#	connUser.sendall('RBR EOF')
				if(not fileExists):
					connUser.sendall('RBR EOF')
				else:
					cwd = cwd + '/' + directory
					nFiles = 0
					#list_files = []
					os.chdir(cwd)
					cwd = os.getcwd()
					list_files = os.listdir(cwd)
					nFiles = len(list_files)
					element = 'RBR ' + str(nFiles) + ' '
					connUser.sendall(element)
					for file in os.listdir(cwd):
						created= os.stat(file).st_ctime
						date_time = datetime.datetime.fromtimestamp(created)
						size = os.stat(file).st_size
						string = str(date_time).split()
						date = string[0][8]+string[0][9]+'.'+string[0][5]+string[0][6]+'.'+string[0][0]+string[0][1]+string[0][2]+string[0][3]
						time = string[1][0]+string[1][1]+string[1][2]+string[1][3]+string[1][4]+string[1][5]+string[1][6]+string[1][7]
						element = file + ' ' + date + ' ' + time + ' ' + str(size) + ' '
						#list_files.append() nao e append mas sim enviar com espaços
						connUser.sendall(element)
						f = open(file,'rb')
						l = f.read(1024)
						while (l):
							connUser.send(1024)
							l = f.read(1024)
						f.close()
				#send files from directory to user
				#for each file nFiles=nFiles+1
				#each file details to send to user: file_name, date_time, size, data (file contents)
        else:
			print "ERR"
			sock.close()
			sockUser.close()

parse()
