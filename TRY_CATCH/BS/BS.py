"""
everything related to the backup server 

"""
import socket
import sys
import os
import time
import shutil

#numero do grupo
GN = 79

BSPORT = 59000 #usar na comunicacao BS - user
CSPORT = 58000 + GN #usar na comunicacao BS - CS
CSNAME = ""

BSNAME = socket.gethostname()


def nextWord(connUser):
	word = ''
	while 1:
		char = connUser.recv(1)
		if((char == ' ' or char =='\n') and word != ''):
			break
		if(not(word == '' and char == ' ')):
			word = word + char
	print 'word:' +word
	return word



def register_user(username,password):
	try:
		user_file = 'user_' + username + '.txt'
		file = open(user_file, 'w')
		file.write(password)
		file.close()
		cwd = os.getcwd()
		user_dir = 'user_' + username
		user_dir_path = cwd + '/' + user_dir
		os.makedirs(user_dir_path)
	except (IOError, OSError),e:
		return

#handles flag values
def create_backup_server():

	l=len(sys.argv)
	global BSPORT
	global CSNAME
	global CSPORT
	i = 1
	try:
		while i < l:  
			if sys.argv[i] == '-b':
				BSPORT = int(sys.argv[i+1])
			if sys.argv[i] == '-n':
				CSNAME = sys.argv[i+1]
			if sys.argv[i] == '-p':
				CSPORT = int(sys.argv[i+1])
			i = i + 2
	except IndexError,e:
		print e
		return
#atencao tem de se acrescentar o \n no final do ok!!!!!
def handlerRGR(status):
	if( status != 'OK'):
		print 'RGR ERR'   #QUAL E A MENSAGEM DE REGISTO NAO POSSIVEL? - CONFIRMAR


def parseTCP():
	try:
		current_user = ''
		current_pass = ''
		# Create a TCP socket (user)
		try:
			sockUser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockUser.bind((BSNAME, BSPORT))
			sockUser.listen(1)
			connUser, addrUser = sockUser.accept()
		except (socket.error,socket.gaierror),e:
			sockUser.close()
			return
		#missingCommand = False
		#dataUser = ''

		while 1:
			
			if(connUser == ''):
				try:
					connUser, addrUser = sockUser.accept()
				except socket.error,e:
					sockUser.close()
					return
			requestUser = nextWord(connUser)
			print 'request: ' + requestUser
			if (requestUser == 'AUT'):
				us = nextWord(connUser)
				pa = nextWord(connUser)
				user_file = 'user_' + us + '.txt'
				try:
					file = open(user_file, 'r')
					password = file.read()
				except IOError,e:
					sockUser.close()
					return
				if(pa == password):
					try:
						connUser.sendall("AUR OK\n")
					except socket.error,e:
						sockUser.close()
						return
					current_user = us
					current_pass = pa
					print 'User: '+str(current_user)
				else:
					try:
						connUser.sendall("AUR NOK")
					except socket.error,e:
						sockUser.close()
						return

			elif (requestUser == 'UPL'):
				dir_name = nextWord(connUser)
				num_files = int(nextWord(connUser))
				try:
					cwd = os.getcwd()
					user_dir = 'user_' + current_user
					user_dir_path = cwd + '/' + user_dir
					dir_path = user_dir_path + '/' + dir_name
					if (not dir_name in os.listdir(user_dir_path)):
						os.makedirs(dir_path)
					os.chdir(dir_path) #open directory
					i = 0
					while (i < num_files):
						filename = nextWord(connUser)
						print 'filename:' + filename
						date = nextWord(connUser)
						print 'date:' + date
						time = nextWord(connUser)
						print 'time:' + time
						size = int(nextWord(connUser))
						print 'size:' + str(size)
						f = open(filename, 'w') #append so I can write data more than once
						dataUPL = connUser.recv(size) #receive data from file
						print dir_name + ': ' + filename + ' ' + str(size) + ' Bytes received'
						f.write(dataUPL)
						i = i + 1
						f.close()
					connUser.sendall('UPR OK')
					os.chdir(cwd) #close directory
					#UPL NOK?
					connUser = ''
				except (IOError,OSError,socket.error),e:
					sockUser.close()
					return
				
			elif (requestUser == 'RSB'):
				
				directory = nextWord(connUser)
				try:
					cwd = os.getcwd() #path of current working directory
					cwd = cwd + '/' + directory
					if(not os.path.exists(cwd)):
						connUser.sendall('RBR EOF')
					else:
						os.chdir(cwd) #open directory
						cwd = os.getcwd()
						list_files = os.listdir(cwd)
						nFiles = len(list_files)
						element = 'RBR ' + str(nFiles) #reply
						connUser.sendall(element)
						for file in list_files:
							created= os.stat(file).st_mtime
							size = os.stat(file).st_size
							date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(created))
							element =' ' + file + ' ' + date_time + ' ' + str(size) + ' '
							connUser.sendall(element) #file details
							f = open(file,'rb')
							l = f.read(size)
							connUser.sendall(l)
							f.close()
						connUser.sendall('\n')
					connUser = ''
				except (OSError,IOError,socket.error),e:
					print "ERR"
					sockUser.close()
	except (socket.error,IOError,OSError,IndexError),e:
		print "ERR"
		sockUser.close()

def parseUDP():
	
	# Create a UDP socket (CS)
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = (BSNAME, CSPORT)
		message = 'REG ' + str(BSPORT) + ' ' + BSNAME
		sock.sendto(message, server_address)
		sock.close()
	except (socket.error,socket.gaierror),e:
		print "ERR"
		sock.close()
		return
	#messages from CS
	try:
		sockBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = (BSNAME, BSPORT)
		sockBS.bind(server_address)
	except (socket.error,socket.gaierror),e:
		print "ERR"
		sockBS.close()
		return

	while 1:
		try:
			data, addr = sockBS.recvfrom(1024)
		except socket.error,e:
			print "ERR"
			sockBS.close()
			return
		command = data.split()
		main_comand = command[0]
		

		if(main_comand == "RGR"):
			handlerRGR(command[1])
		elif(main_comand == "UAR"):
			if(not command[1] == 'OK'):
				print 'UAR ERR'
		elif(main_comand == "LSF"):
			user = command[1]
			directory = command[2]
			try:
				cwd = os.getcwd() #path of current working directory
				path = cwd + '/user_' + user + '/' + directory
				if(os.path.exists(cwd)):
					os.chdir(path) #open directory
					list_files = os.listdir(path)
					nFiles = len(list_files)
					element = 'LFD ' + str(BSPORT) + ' ' + BSNAME + ' ' + str(nFiles)  #reply
					#sockBS.sendto(element, addr) #LFD portBS IPBS N 
				
					print str(list_files)
					for f in list_files:
						print f
						created= os.stat(f).st_mtime
						size = os.stat(f).st_size
						date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(created))
						element = element + ' ' + f + ' ' + date_time + ' ' + str(size)
						#sockBS.sendto(element, addr)
					element = element + '\n'
					sockBS.sendto(element, addr)

					os.chdir(cwd) #close directory
			except (OSError,IOError,socket.error),e:
				sockBS.close()
				return


		elif(main_comand == "LSU"):
			try:
				if (len(command)== 3):
					user = str(command[1])
					passw = str(command[2])
					print 'aqui '
					user_file = 'user_' + user + '.txt'
					cwd = os.getcwd()
					if(not user_file in os.listdir(cwd)):
						register_user(user,passw)
						print 'New user: ' + user
					sockBS.sendto('LUR OK\n', addr)
					#sockBS.close()
				else:
					sockBS.sendto('LUR ERR', addr)
			except (OSError,IOError,socket.error),e:
				sockBS.close()
				return
		elif(main_comand == "DLB"):
			user = command[1]
			directory = command[2]
			try:
				cwd = os.getcwd()
				user_dir = cwd + '/user_' + user
				dir_path = user_dir + '/' + directory
				if(os.path.isdir(dir_path)):
					shutil.rmtree(dir_path)
					if (len(os.listdir(user_dir)) == 0):
						shutil.rmtree(user_dir)
						user_file_path = cwd + '/user_' + user + '.txt'
						os.remove(user_file_path)
					sockBS.sendto('DBR OK\n', addr)
				else:
					sockBS.sendto('DBR NOK\n', addr)
				
			except (OSError,IOError,socket.error),e:
				sockBS.close()
				return

		
create_backup_server()
try:
	pid = os.fork()
	if(pid == 0):
		while(1):
			parseTCP() # o filho vai tratar de responder a todos os pedidos TCP
	else:	
		parseUDP()	# o pai vai tratar de responder a todos os pedidos UDP
except OSError,e:
	print "ERR"