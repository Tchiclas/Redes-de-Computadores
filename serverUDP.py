import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('', 58063)
sock.bind(server_address)
#print 'fiz bind em port 10000'
while True:
    #print '\nwaiting to receive message'
    data, address = sock.recvfrom(4096)
    
    #print 'received' + str(len(data)) + 'bytes from ' + str(address)
    print data
    
    #if data:
    sock.sendto('RGR OK', address)
    #print 'enviei de volta'