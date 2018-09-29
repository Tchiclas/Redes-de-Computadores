'''
everything related to the central server 

'''
import socket
import sys
import os

#o valor generico sera 58000 mais o numero do grupo
GN = 99  #GN sera o numero do grupo

HOST = socket.gethostname()
PORT = 58000 +GN

#dicionario com o username como key
# taamebem tem info de se tem ficheiros no BS ou nao para
#quando faz o pedido de deluser validar logo se e possivel
users = dict()
users = {"12345":["aaaaaaaa"],}        #utilizador para teste

#dicionario com o ip dos BS como key
BS = {}


#lista de diretorias 


#------chamar no inicio
def parse():
	global PORT
	IPBS = 0
	portBS = 0
	#definir o PORT
	if(len(sys.argv) != 1 and sys.argv[1] == "-p"):
		PORT = int(sys.argv[2])
		
	"""
	#socket BS - CS (UDP) =========================================
	sockBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ("", PORT)
	sockBS.bind(server_address)
	"""
	
	current_user = ''
	current_pass = ''
	while 1:
		
		#socket USER - CS (TCP) ======================================
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("", PORT))
		s.listen(1)
		conn, addr = s.accept()
		#receive from user
		string = conn.recv(4096)
		data = string.split()

		"""
		#receive from BS
		dataBS, address = sockBS.recvfrom(4096)
		commandBS = dataBS.split()
		print dataBS
		"""

		commandBS = ['so para nao dar erro']

		if(data[0] == "AUT"):
			username = data[1]
			password = data[2]
			if(users.has_key(str(username))):
				if(users[str(username)] == str(password)):
					current_user = str(username)
					current_pass = str(password)
					conn.sendall("AUR OK")
					print 'User: '+str(username)
				else:
					conn.sendall("AUR NOK")
			else:
				users[str(username)] = str(password)
				conn.sendall("AUR NEW")
				print 'New user: ' + str(username) #imprime o username

		
		elif(data[0] == "DLU"):
			print "DLU"

		# tem de se fazer verificacao se pedido esta ok ou nao
		elif(data[0] == "BCK"):
			num_files = str(data[2])
			i = 3
			file_lst = ''
			#users[current_user].append(1) # 1 == user has files stored in BS
			#verifies num files < 20 and stores the list to resend to user
			if (num_files <= 20):
				while i < num_files:
					file_lst = file_lst + str(data[i])
					i = i + 1
			else:
				while i < 20:
					file_lst = file_lst + str(data[i])
					i = i + 1
			
			print 'BCK ' + current_user + ' ' + str(data[1]) + ' ' + str(IPBS) + ' '+str(portBS) 
			#send request LSU to BS
			send_request = 'LSU ' + current_user + current_pass
			#sockBS.sendto(send_request, address)
			#dataBS, address = sockBS.recvfrom(4096) #LUR OK

			#if (dataBS == 'LUR OK'):
			m = 'BKR '+str(IPBS)+' '+str(portBS) + ' '+ num_files + ' ' + file_lst
				
			#elif (dataBS == 'LUR NOK'):
				#m = 'BKR EOF' #no more space in existing BS
			# else if o formato do pedido estiver mal BKR ERR
			conn.sendall(m)
		elif(data[0] =="RST"):
			print "RST"
		elif(data[0] == "LSD"):

			counter = 0
			rec = ""
			file = open("backup_list.txt","r")
			for line in file:
				split = line.split()
				print split
				if(str(split[0]) == str(username)):
					counter = counter +1
					rec = rec +" "+ str(split[1])
			file.close()

			rec = "LDR "+ str(counter) +rec + "\n"
			conn.sendall(rec)
			print rec

		elif(data[0] == "LSF"):
			print "LSF"
		elif(data[0] == "DEL"):
			print "DEL"
		elif(data[0] == "OUT"):
			print "OUT"
			break

		#requests from BS

		if(commandBS[0] == "REG"):       
			#global IPBS = data[1]
			#global portBS = data[2]
			#bs[str(ip)] == int(port)
			sockBS.sendto('RGR OK', address)
		elif (commandBS[0] == 'UNR'):
			IPBS = commandBS[1]
			portBS = int(commandBS[2])
			stop_BS_operations(IPBS , portBSs)
		elif (commandBS[0] == 'LFD'):
			num_files = int(commandBS[1])
			if (num_files > 0):
				l = len(commandBS)
				i = 2
				while i < l:
					file_name = str(commandBS[i])
					date = str(commandBS[i+1]) + str(commandBS[i+2])
					size = str(commandBS[i+3])
					print file_name + ' ' + date + ' ' + size
					i = i + 4
		elif (commandBS[0] == 'LUR'):
			if (commandBS[1] != 'OK\n'):
				print 'LUR ERR'
		elif (commandBS[0] == 'DBR'):
			if (commandBS[1]!= 'OK\n'):
				print 'DBR ERR'
		"""
		else:
			print "ERR"
			print 'Received', repr(data)
		"""
		#conn.sendall(data)
		s.close()
	#sockBS.close()


parse()

#vai ter um ficheiro backup_list.txt e BS_list.txt 

#backup_list vai ter uma lista de todos os ficheiros 
#backedup do utilizador que esta logged in com o nome e sitio onde estao ? 


#BS_list lista dos backup servers registados tbm podia
#ser representado num dicionario com o ip e a porta
