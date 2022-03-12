import socket
import threading
import time

def on_new_client_recv(connection_socket, caddr):
    while True:
        cmsg = connection_socket.recv(1024)
        cmsg = cmsg.decode()
        print(cmsg)

def on_new_client_send(connection_socket, caddr):
    cmsg = "Hi"
    while True:
        connection_socket.send(cmsg.encode())
        time.sleep(3)

server_port = 12000
server_ip = 'localhost'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server_socket.bind((server_ip,server_port))
server_socket.listen(5)

print('Server running on port ', server_port)

#Now the main server loop
while True:
    connection_socket, caddr = server_socket.accept()
    threading.Thread(target=on_new_client_recv, args=(connection_socket,caddr)).start()
    threading.Thread(target=on_new_client_send, args=(connection_socket,caddr)).start()
        
