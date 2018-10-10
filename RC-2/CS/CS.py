'''
everything related to the central server 
user_dir = cwd + '/user_' + username
os.makedirs(user_dir)

'''
import socket
import signal
import sys
import os
import shutil
import time

#o valor generico sera 58000 mais o numero do grupo
GN = 79  #GN sera o numero do grupo

HOST = socket.gethostname()
PORT = 58000 +GN
lastBS = -2



#dicionario com o username como key
#users = {"12345":"aaaaaaaa"}        utilizador para teste


def signal_term_handler(signal, frame):
    print 'got SIGTERM'
    sys.exit(0)

def parseUDP():
	sockBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ("", PORT)
	sockBS.bind(server_address)
	print ' socket criado'
	while(1):
		#receive from BS
		dataBS, address = sockBS.recvfrom(4096)
		print 'recebi ' + dataBS
		commandBS = dataBS.split()
		
		if(commandBS[0] == "REG"):
			if(not len(commandBS) == 3):
				sockBS.sendto("RGR ERR\n", (address))
			else:
				portname = commandBS[2]
				portnum = commandBS[1]
				print portname + ' ' + portnum
				exists = False  #BS is already registed
				if("BS_list.txt" in os.listdir(os.getcwd())):
					BS = open("BS_list.txt","r")
					line = BS.read()
					split = line.split()
					index = 0
					length = len(split)
					while index < length:
						if(split[index] == portnum): # se tiver uma porta igual 
							exists = True
						index = index + 2
					BS.close()
					if (not exists):
						BS = open("BS_list.txt","a")
						BS.write(" "+portnum+" "+ portname)
						BS.close()
				else:
					BS = open("BS_list.txt","w")
					BS.write(portnum+" "+ portname)
					BS.close()

				#sockBS.sendto("RGR NOK\n", (address))

				print '+BS: ' + portname + ' ' + portnum
				sockBS.sendto("RGR OK\n", (address))

			

def user_ver(username,password):

	cwd = os.getcwd()
	list_dir = os.listdir(cwd)
	user_file = 'user_' + username + '.txt'
	if user_file in list_dir:
		file = open(user_file, 'r')
		user_pass = file.read()
		if (user_pass == password):
			print 'User: ' + username
			return "AUR OK\n"
		else:
			return "AUR NOK\n"
		file.close()
	else:
		file = open(user_file, 'w')
		file.write(password)
		file.close()
		print 'New user: ' + username
		return "AUR NEW\n"
			


	
#------chamar no inicio
def parseTCP(conn):
	
	global lastBS

	#receive from user
	string = conn.recv(4096) #receive login
	data = string.split()
	print data

	username = data[1]
	password = data[2]
	conn.sendall(user_ver(username,password)) #AUR

	string = conn.recv(4096) #receive command

	data = string.split()
	#print data

	try:
		command = data[0]
	except IndexError:
		return

	if(data[0] == "DLU"):
		cwd = os.getcwd()
		user_dir = cwd + '/user_' + username
		user_file = cwd + '/user_' + username + '.txt'
		if (user_dir in os.listdir(cwd)): #user has dir
			if (len(os.listdir(user_dir)) == 0):
				os.remove(user_dir)
				os.remove(user_file)
				conn.sendall("DLR OK\n")
			else:
				conn.sendall("DLR NOK\n")
		else:
			os.remove(user_file)
			conn.sendall("DLR OK\n")
		print "\tDeleted"
		return

	elif(data[0] == "BCK"):
		print data
		if (len(data) < 3):
			conn.sendall("BKR ERR\n")
		else:
			n_files = int(data[2])
			if(not len(data) == 3+4*n_files):
				conn.sendall("BKR ERR\n")
			else:
				directory = data[1]
				n_files = int(data[2])
				cwd = os.getcwd()
				user_dir = 'user_' + username #user directory
				user_dir_path = cwd + '/' + user_dir #path of user directory
				directory_path = user_dir_path+'/'+directory #path of directory
				list_dir = os.listdir(cwd) #list of directories in cwd
				list_files = data[3:] #list of files to backup
				#list_dir_files = os.listdir(directory_path) #list of files in directory
				#user has backup in BS
				if (user_dir in list_dir):
					if(directory in os.listdir(user_dir_path)):
						#if('IP_port.txt' in os.listdir(directory_path))
						ip_file = directory_path + '/IP_port.txt'
						file = open(ip_file, 'r')
						file_data = file.read() #portnum portname
						line = file_data.split()
						IPBS = line[1]
						portBS = line[0]
						file.close()
						print 'BCK ' + username + ' ' + directory + ' ' + IPBS +' '+ portBS
						#LSF request to BS
						sockBCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
						server_address = (IPBS, int(portBS))
						message = "LSF " + username + ' ' + directory + '\n'
						sockBCK.sendto(message, server_address) #nao sei se preciso de criar um socket ou nao
				
						print 'estou aqui'
						dataLSF, address = sockBCK.recvfrom(4096)
						print 'dataLSF: ' + dataLSF
						reply = dataLSF #LSF reply
						i = 0
						splitLSF = dataLSF.split()
						n = int(splitLSF[3])
						print str(n)
						""" while i < n:
							dataLSF, address = sockBCK.recvfrom(4096)
							reply = reply + dataLSF
							#print 'reply: ' + reply
							i = i + 1 """
						sockBCK.close()
						print 'reply:' + reply
						reply = reply.split()
						length = len(list_files)
						i = 0
						answer = []
						new_n_files = 0
						print str(list_files)
						while i < length:
							f = list_files[i] #filename
							if (f in reply):
								i_r = reply.index(f)
								d_r = time.strptime(reply[i_r+1], "%d.%m.%Y") 
								t_r = time.strptime(reply[i_r+2], "%H:%M:%S")
								s_r = reply[i_r+3]
								d = time.strptime(list_files[i+1], "%d.%m.%Y") 
								t = time.strptime(list_files[i+2], "%H:%M:%S")
								size = list_files[i+3]
								if(size!=s_r or d>d_r):
									answer = answer + list_files[i:i+4]
									new_n_files = new_n_files + 1
								elif(d==d_r and t>t_r):
									answer = answer + list_files[i:i+4]
									new_n_files = new_n_files + 1
							else:
								answer = answer + list_files[i:i+4]
								new_n_files = new_n_files + 1
							print 'i: ' + str(i) + ' answer: ' + str(answer)
							i = i + 4
						answer = ' '.join(answer)
						n_files = new_n_files
					else:
						if(not 'BS_list.txt' in list_dir):
							conn.sendall("BKR EOF\n")
						else:
							#user and directory dir
							os.makedirs(directory_path)

							BS = open("BS_list.txt","r")
							line = BS.read()
							line = line.split()
							index = lastBS + 2
							length = len(line)
							if(not index < length):
								index = 0
							portBS = line[index]
							IPBS = line[index+1]
							fileIP = open(directory_path+'/IP_port.txt', 'w')
							fileIP.write(portBS + ' ' + IPBS)
							fileIP.close()
							lastBS = index
							print 'BCK ' + username + ' ' + directory + ' ' + IPBS +' '+ portBS
							#LSU request to BS
							print 'vou enviar LSU'
							sockBCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
							server_address = (IPBS, int(portBS))
							print 'server_address: ' +  str(server_address)
							sockBCK.sendto("LSU " + username + ' ' + password , server_address)
							print 'enviei LSU'
							dataLSU, address = sockBCK.recvfrom(1024)
							sockBCK.close()
							print 'dataLSU: ' + dataLSU
							if(dataLSU == 'LUR ERR'):
								conn.sendall("BKR ERR\n")
							elif(dataLSU == 'LUR NOK'):
								conn.sendall("BKR EOF\n")
							else:
								answer = ' '.join(list_files)
								
					answer = 'BKR ' + IPBS + ' ' + portBS + ' ' + str(n_files) + ' ' + answer + '\n'
					conn.sendall(answer)

				else:
					if(not 'BS_list.txt' in list_dir):
						conn.sendall("BKR EOF\n")
					else:
						#user and directory dir
						os.makedirs(user_dir_path)
						os.makedirs(directory_path)

						BS = open("BS_list.txt","r")
						line = BS.read()
						line = line.split()
						index = lastBS + 2
						length = len(line)
						if(not index < length):
							index = 0
						portBS = line[index]
						IPBS = line[index+1]
						fileIP = open(directory_path+'/IP_port.txt', 'w')
						fileIP.write(portBS + ' ' + IPBS)
						fileIP.close()
						lastBS = index
						print 'BCK ' + username + ' ' + directory + ' ' + IPBS +' '+ portBS
						#LSU request to BS
						print 'vou enviar LSU'
						sockBCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
						server_address = (IPBS, int(portBS))
						print 'server_address: ' +  str(server_address)
						sockBCK.sendto("LSU " + username + ' ' + password , server_address)
						print 'enviei LSU'
						dataLSU, address = sockBCK.recvfrom(1024)
						sockBCK.close()
						print 'dataLSU: ' + dataLSU
						if(dataLSU == 'LUR ERR'):
							conn.sendall("BKR ERR\n")
						elif(dataLSU == 'LUR NOK'):
							conn.sendall("BKR EOF\n")
						else:
							answer = ' '.join(list_files)
				answer = 'BKR ' + IPBS + ' ' + portBS + ' ' + str(n_files) + ' ' + answer + '\n'
				conn.sendall(answer)
						
	elif(data[0] =="RST"):
		print "RST"

	elif(data[0] == "LSD"):
		rec = ""
		counter = 0
		if(not os.path.isdir(os.getcwd()+'/user_' + username)):
			conn.sendall("LDR 0\n")
			return
		listdir = os.listdir(os.getcwd()+'/user_' + username)
		for diri in listdir:
			rec += " "+diri
			counter += 1

		rec = "LDR "+ str(counter) +rec + "\n"
		conn.sendall(rec)

	elif(data[0] == "LSF"):
		#vai ao ficheiro backup_list ver qual e o BS que tem a diretoria que se quer
		BSip = ""
		BSport = ""

		cwd = os.getcwd()
		path = cwd +"/user_"+username + "/" + data[1] # command[1] e o nome da diretoria
		file = open(path+"/IP_port.txt","r")

		for line in file:
			split = line.split()
			BSip = split[1]
			BSport = split[0]
		file.close()
		#pergunta ao BS que tem a diretoria que ficheiros tem
		sockBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		address = (BSip,int(BSport))

		sockBS.sendto(data[0]+" "+username+" "+data[1]+"\n", (address))

		#recebe LFD BSip BSport N (filename date_time size)*
		dataBS, address = sockBS.recvfrom(4096)	
		sockBS.close()


		#reencaminha LFD para o user
		conn.sendall(dataBS)

		print "LSF"
	elif(data[0] == "DEL"):
		directory = data[1]
		print "DEL"
		cwd = os.getcwd()
		user_dir = cwd + '/user_' + username
		dir_path = user_dir + '/' + directory
		file_ip = dir_path + '/IP_port.txt'
		file = open(file_ip, 'r')
		file_data = file.read() #portnum portname
		line = file_data.split()
		IPBS = line[1]
		portBS = line[0]
		file.close()
		sockDLB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = (IPBS, int(portBS))
		messageDLB = 'DLB ' + username + ' ' + directory + '\n'
		sockDLB.sendto(messageDLB, server_address) #DLB request
		dataDLB, address = sockDLB.recvfrom(4096) #DBR OK
		sockDLB.close()
		if(dataDLB == 'DBR OK\n'):
			try:
				shutil.rmtree(dir_path)
				conn.sendall('DDR OK\n')
			except IOError, e:
				conn.sendall('DDR NOK\n')
		else:
			print 'Could not delete ' + directory
			conn.sendall('DDR NOK\n')
		



	


if(len(sys.argv) != 1 and sys.argv[1] == "-p"):
		PORT = int(sys.argv[2])
pid = os.fork()
if(pid == 0):
	#signal.signal(signal.SIGINT, signal_term_handler)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", PORT))
	s.listen(1)
	while(1):
		conn, addr = s.accept()
		childpid = os.fork()
		if(childpid == 0):
			parseTCP(conn) # o filho vai tratar de responder a todos os pedidos TCP
			s.close()
			break;
else:
	#signal.signal(signal.SIGINT, signal_term_handler)
	parseUDP()	# o pai vai tratar de responder a todos os pedidos UDP


#ps aux e dps kill -9

