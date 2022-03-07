import subprocess
import socket
import threading
import time

def send_on_jtag(msg):
    #assert len(msg)>=1, "Please make the cmd a single character"

    output = subprocess.Popen("nios2-terminal", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    #output.stdin.write(bytearray(str(cmd + "\n"), 'utf-8'))
    #output.stdin.flush()

    vals = output.stdout.readlines() 

    return vals[4]

def perform_computation():
    res = send_on_jtag()
    print(res)

def send_data(client_socket, data):
    while True:
        client_socket.send(data.encode())
        time.sleep(3)

def recv_data(client_socket):
    while True:
        msg = client_socket.recv(1024)
        print(msg.decode())

#the server name and port client wishes to access
server_name = 'localhost'
server_port = 12000

#create a TCP client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_name, server_port))

#some work
threading.Thread(target=send_data, args=(client_socket,"2")).start()
threading.Thread(target=recv_data, args=(client_socket,)).start()

