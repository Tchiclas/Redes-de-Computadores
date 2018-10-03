'''
everything related to the central server 

'''
import socket
import sys
import os

#o valor generico sera 58000 mais o numero do grupo
GN = 63  #GN sera o numero do grupo

HOST = socket.gethostname()
PORT = 58000 +GN



#dicionario com o username como key
users = {"12345":"aaaaaaaa"}        #utilizador para teste


def parseUDP():


	sockBS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sockBS.bind(("", 58063))
	
	while(1):
				#receive from BS
		dataBS, address = sockBS.recvfrom(4096)

		commandBS = dataBS.split()
		print "dataBS: "+dataBS+" address: "
		if(commandBS[0] == "REG"):
			exists = False
			BS = open("BS_list.txt","r")
			for line in BS:
				split = line.split()
				if(split[0] == commandBS[1]): # se tiver uma porta igual 
					exists = True

			BS.close()
			if(not exists):
				BS = open("BS_list.txt","a")
				BS.write(commandBS[1]+" "+ commandBS[2]+"\n")
				BS.close()
				#sendto BS RGR OK\n
				sockBS.sendto("RGR OK\n", (commandBS[2],int(commandBS[1])))
			else:
				sockBS.sendto("RGR NOK\n", (commandBS[2],int(commandBS[1])))

def user_ver(username,password):

	file = open("users_list.txt","r")
	for line in file:
		split = line.split()
		if(split[0] == str(username)):
			if(split[1] == str(password)):
				return "AUR OK\n"
			else:
				return "AUR NOK\n"
	file.close()

	file = open("users_list.txt","a")
	file.write(username+" "+ password+"\n")
	file.close()
	return "AUR NEW\n"
			


	
#------chamar no inicio
def parseTCP():
	global PORT
	#IPBS = 0
	#portBS = 0
	#definir o PORT
	if(len(sys.argv) != 1 and sys.argv[1] == "-p"):
		PORT = int(sys.argv[2])

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", PORT))
	s.listen(1)
	conn, addr = s.accept()
	#receive from user
	string = conn.recv(4096)
	data = string.split()

	if(data[0] == "AUT"):
		conn.sendall(user_ver(data[1],data[2]))
	else:
		conn.sendall("ERR")
		
	s.close()
	while 1:
		#socket USER - CS (TCP) ======================================

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("", PORT))
		s.listen(1)
		conn, addr = s.accept()

		#receive from user
		string = conn.recv(4096)
		data = string.split()
		print data

		username = data[1]
		password = data[2]
		conn.sendall(user_ver(username,password))

		string = conn.recv(4096)
		data = string.split()
		print data

		if(data[0] == "DLU"):
			ok = True
			file = open("backup_list.txt","r")
			for line in file:
				split = line.split()
				if(split[0] == str(username)):
					ok = False
			file.close()

			if(not ok):
				file = open("users_list.txt","r")
				lines = file.readlines()
				file.close()

				file = open("users_list.txt","w")
				for line in lines:
					if(str(username) not in line):
						file.write(line)
				file.close()

				conn.sendall("DLR OK\n")
				s.close()
				return	
			else:
				conn.sendall("DLR NOK\n")  #nao existia esse user sequer i guess


			print "DLU"
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
			s.close()
			return

		s.close()


pid = os.fork()
if(pid == 0):
	while(1):
		parseTCP() # o filho vai tratar de responder a todos os pedidos TCP
else:
	parseUDP()	# o pai vai tratar de responder a todos os pedidos UDP


#ps aux e dps kill -9
