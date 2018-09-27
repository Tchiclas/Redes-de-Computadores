import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('194.210.231.86/23', 10000)
message = 'This is the message.  It will be repeated.'



# Send data
print 'sending messge'
sent = sock.sendto(message, server_address)

# Receive response
print 'waiting to receive'
data, server = sock.recvfrom(4096)
print 'received: ' + data


print 'closing socket'
sock.close()