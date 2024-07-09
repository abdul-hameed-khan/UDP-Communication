
import socket


UDP_IP = "127.0.0.1"
UDP_PORT = 5005

MESSAGE = "This is Port No 5005 sending you a message" 


# MESSAGE = b"Hello, World!" 

'''message should be sent in Bytes. to do this write b before string line b"hello" or 
 use .encode() function with message avariable'''


# print("UDP target IP: %s" % UDP_IP)
# print("UDP target port: %s" % UDP_PORT)

print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # For IPv4 protocol
                     socket.SOCK_DGRAM) # For UDP connection

sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
sock.close()



    