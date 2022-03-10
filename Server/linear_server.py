import socket
import time

def on_new_client_recv(connection_socket, caddr):
    try:
        cmsg = connection_socket.recv(1024)
        cmsg = cmsg.decode()
        if cmsg == "":
            connection_socket.close()
        print(cmsg)
    except:
        pass

def on_new_client_send(connection_socket, caddr):
    global cmsg
    try:
        connection_socket.send(str(cmsg).encode())
        print(f"sent {str(cmsg)}")
    except:
        pass
    cmsg += 1

server_port = 12000
server_ip = 'localhost'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip,server_port))
server_socket.settimeout(0.01)
server_socket.listen(5)
cmsg = 10

print('Server running on port ', server_port)

connection_sockets = [None in range(5)]
caddr = [None in range(5)]
i = 0
#Now the main server loop
while True:
    try:
        connection_sockets[i], caddr[i] = server_socket.accept()
        i += 1
    except: pass
    for i, socket in enumerate(connection_sockets):
        if socket != None:
            on_new_client_recv(socket,caddr[i])
            on_new_client_send(socket,caddr[i])
