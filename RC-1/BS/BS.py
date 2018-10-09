"""
everything related to the backup server 

"""
import socket
import sys
import os
import time
import shutil

#numero do grupo
GN = 78

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
		word = word + char
	print 'word: ' +word
	return word



	




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


def parseTCP():
	current_user = ''
	current_pass = ''
	# Create a TCP socket (user)
	sockUser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockUser.bind((BSNAME, BSPORT))
	sockUser.listen(1)
	connUser, addrUser = sockUser.accept()
	#missingCommand = False
	#dataUser = ''

	while 1:
		
		if(connUser == ''):
			connUser, addrUser = sockUser.accept()
		requestUser = nextWord(connUser)
		print 'request: ' + requestUser
		if (requestUser == 'AUT'):
			print 'hey'
			us = nextWord(connUser)
			print 'user: ' + us
			pa = nextWord(connUser)
			print 'pass: ' + pa
			user_file = 'user_' + us + '.txt'
			file = open(user_file, 'r')
			password = file.read()
			if(pa == password):
				connUser.sendall("AUR OK\n")
				current_user = us
				current_pass = pa
				print 'User: '+str(current_user)
			else:
				connUser.sendall("AUR NOK")

		elif (requestUser == 'UPL'):
			dir_name = nextWord(connUser)
			print 'dir_name: ' + dir_name
			num_files = int(nextWord(connUser))
			print 'num_files: ' + str(num_files)
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
				print 'filename: ' + filename
				date = nextWord(connUser)
				print 'date: ' + date
				time = nextWord(connUser)
				print 'time: ' + time
				size = int(nextWord(connUser))
				print 'size: ' + str(size)
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
			
		elif (requestUser == 'RSB'):
			#if (not len(requestUser) == 2):
			#	connUser.sendall('RBR ERR')
			#else:
			directory = nextWord(connUser)
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
        else:
			print "ERR"
			#sock.close()
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
		#print data
		command = data.split()

		

		if(command[0] == "RGR"):
			handlerRGR(command[1])
		elif(command[0] == "UAR"):
			if(not command[1] == 'OK'):
				print 'UAR ERR'
		elif(command[0] == "LSF"):
			user = command[1]
			directory = command[2]
			cwd = os.getcwd() #path of current working directory
			cwd = cwd + '/user_' + user + '/' + directory
			if(os.path.exists(cwd)):
				#os.chdir(cwd) #open directory
				#cwd = os.getcwd()
				list_files = os.listdir(cwd)
				nFiles = len(list_files)
				element = 'LFD ' + str(BSPORT) + ' ' + BSNAME + ' ' + str(nFiles)  #reply
				sockBS.sendto(element, addr) #LFD portBS IPBS N 
			
				print str(list_files)
				for f in list_files:
					print f
					created= os.stat(f).st_mtime
					size = os.stat(f).st_size
					date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(created))
					element =  ' ' + f + ' ' + date_time + ' ' + str(size)
					sockBS.sendto(element, addr)
				sockBS.sendto('\n', addr)

		elif(command[0] == "LSU"):
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
		elif(command[0] == "DLB"):
			user = command[1]
			directory = command[2]
			cwd = os.getcwd()
			user_dir = cwd + '/user_' + user
			dir_path = user_dir + '/' + directory
			try:
				shutil.rmtree(dir_path)
				sockBS.sendto('DBR OK\n', addr)
			except IOError, e:
				sockBS.sento('DBR NOK\n', addr)
				#Devia existir algum else aqui?

		
create_backup_server()
pid = os.fork()
if(pid == 0):
	while(1):
		parseTCP() # o filho vai tratar de responder a todos os pedidos TCP
else:
	parseUDP()	# o pai vai tratar de responder a todos os pedidos UDP
