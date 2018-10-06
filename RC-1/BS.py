"""
everything related to the backup server 

"""
import socket
import sys
import os
import time

#numero do grupo
GN = 71

BSPORT = 59000 #usar na comunicacao BS - user
CSPORT = 58000 + GN #usar na comunicacao BS - CS
CSNAME = ""

#dictionary with username as keyword
users = {"12345":"aaaaaaaa"}

#data structure with directories with files

def register_user(username,password):
	user_file = 'user_' + username + '.txt'
	file = open(user_file, 'w')
	file.write(password)
	file.close()

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

def handlerLSF(user, dir, server_address): #NOT DONE!!!!!!
	cwd = os.getcwd() #path of current working directory
    cwd = cwd + '/' + dir
	if(os.path.exists(cwd)):
		os.chdir(cwd) #open directory
		cwd = os.getcwd()
		list_files = os.listdir(cwd)
		nFiles = len(list_files)
		element = 'LFD ' + str(nFiles)  #reply
		connUser.sendall(element)
		for file in list_files:
			created= os.stat(file).st_ctime
			size = os.stat(file).st_size
			date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(created))
			element =  ' ' + file + ' ' + date_time + ' ' + str(size)
			connUser.sendall(element) #file details
		connUSer.sendall('\n')


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
	sockUser.bind(("", BSPORT))
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
			if (len(command= == 3)):
				user = str(command[1])
				passw = str(command[2])
				register_user(user,passw)
				print 'New user: ' + user
				sock.sendto('LUR OK', server_address)
			else:
				sock.sendto('LUR ERR', server_address)
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
						created= os.stat(file).st_ctime
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

parse()
