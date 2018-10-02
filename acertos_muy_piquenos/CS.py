'''
everything related to the central server 

'''
import socket
import sys
import os

#o valor generico sera 58000 mais o numero do grupo
GN = 68  #GN sera o numero do grupo

HOST = socket.gethostname()
PORT = 58000 +GN



#dicionario com o username como key
users = {"12345":"aaaaaaaa"}        #utilizador para teste


def parseUDP():


	sockBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = ("", PORT)
	sockBS.bind(server_address)
	
	while(1):
		#receive from BS
		dataBS, address = sockBS.recvfrom(4096)
		commandBS = dataBS.split()
		if (len(commandBS) < 3 ):
			portname = ''  #como ' ' nao era reconhecido como nome de porta tive de improvisar 
		else:
			portname = commandBS[2]
		
		portnum = commandBS[1]
		
		if(commandBS[0] == "REG"):
			exists = False  #BS is already registed
			BS = open("BS_list.txt","r")
			for line in BS:
				split = line.split()
				if(split[0] == portnum): # se tiver uma porta igual 
					exists = True

			BS.close()
			if(exists):
				BS = open("BS_list.txt","a")
				BS.write(portnum+" "+ portname+"\n")
				BS.close()
				#sendto BS RGR OK\n
				sockBS.sendto("RGR OK\n", (address))
				#print '+BS: ' + portname + ' ' + portnum
			else:
				sockBS.sendto("RGR NOK\n", (address))

			print '+BS: ' + portname + ' ' + portnum
			


	
#------chamar no inicio
def parseTCP():
	global PORT
	#IPBS = 0
	#portBS = 0
	#definir o PORT
	if(len(sys.argv) != 1 and sys.argv[1] == "-p"):
		PORT = int(sys.argv[2])
		

	while 1:
		#socket USER - CS (TCP) ======================================
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("", PORT))
		s.listen(1)
		conn, addr = s.accept()
		#receive from user
		string = conn.recv(4096)
		data = string.split()

		if(data[0] == "AUT"):
			username = data[1]
			password = data[2]

			if(users.has_key(str(username))):

				if(users[str(username)] == str(password)): #se o utilizador e a pass coincidirem
					conn.sendall("AUR OK\n")
					print 'User: '+str(username)

				else: #se a pass para esse utilizador estiver errada
					conn.sendall("AUR NOK\n") 

			else: # se o utlizador nao exisitir
				users[str(username)] = str(password)
				conn.sendall("AUR NEW\n")
				print 'New user: ' + str(username) 

		
		elif(data[0] == "DLU"):
			ok = True
			file = open("backup_list.txt","r")
			for line in file:
				split = line.split()
				if(split[0] == str(username)):
					ok = False
			file.close()
			if(ok):
				conn.sendall("DLR OK\n")
			else:
				conn.sendall("DLR NOK\n")
			# retirar user do discionario de users validos
			del users[username]
		elif(data[0] == "BCK"):
			#send request LSU to BS
			s.close()
			#loop por todos os BS registados para saber qual pode fazer o backup
			for IPBS in BS:
				sockBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sockBS.bind(("", PORT))

				sockBS.sendto('LSU ' + username + " " + password, (IPBS,int(BS[IPBS])))
				dataBS, address = sockBS.recvfrom(4096)
				data = dataBS.split()
				if(data[0] == "LUR"):
					if(data[1] == "OK"):
						#O BS verificou que pode continuar
						print "LUR OK"
					elif(data[1] == "NOK"):
						#algo se passou
						print "LUR NOK"
				else:
					#erro!
					print "ERR"
				sockBS.close()

			#volta a ligar TCP com o user
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(("", PORT))
			s.listen(1)
			conn, addr = s.accept()

			print 'BCK ' + username + ' ' + str(data[1]) + ' ' + str("IPBS")+' '+str(portBS)

			m = 'BKR '+str(IPBS)+' '+str(portBS) + ' '+ str(data[2])
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
			#vai ao ficheiro backup_list ver qual e o BS que tem a diretoria que se quer
			BSip = ""
			BSport = ""

			file = open("backup_list.txt","r")
			for line in file:
				split = line.split()
				print split
				if(str(split[1]) == data[1]):

					BSip = split[2]
					BSport = split[3]
			file.close()
			rec = "LFD "+" "+BSip+" "+BSport
			#recebe LFD BSip BSport N (filename date_time size)*

			#reencaminha LFD para o user
			conn.sendall(rec)

			print "LSF"
		elif(data[0] == "DEL"):
			print "DEL"
		elif(data[0] == "OUT"):
			print "OUT"
			#break


pid = os.fork()
if(pid == 0):
	parseTCP() # o filho vai tratar de responder a todos os pedidos TCP
else:
	parseUDP()	# o pai vai tratar de responder a todos os pedidos UDP

#parseUDP()

#vai ter um ficheiro backup_list.txt e BS_list.txt 

#backup_list vai ter uma lista de todos os ficheiros 
#backedup do utilizador que esta logged in com o nome e sitio onde estao ? 


#BS_list lista dos backup servers registados tbm podia
#ser representado num dicionario com o ip e a porta

#ps aux e dps kill -9
