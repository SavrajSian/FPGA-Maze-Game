import subprocess
from time import sleep
import socket

output = subprocess.Popen("nios2-terminal", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)


def uart(cmd):
    output.stdin.write(bytearray(str(cmd + "\n"), 'utf-8'))                                  
    output.stdin.flush()

    val = output.stdout.readline()

    return val

def perform_computation():
    res = uart("W")
    return res

def main():
    print("We're in tcp client..."); 
    #the server name and port client wishes to access 
    server_name = '3.8.153.58' # FIXME: Put your server ipv4 addr
    #'52.205.252.164' 
    server_port = 12000
    
    while(1):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_name, server_port))
        #some work
        msg = perform_computation()

        #send the message  to the udp server
        client_socket.send(msg)

        #return values from the server
        msg = client_socket.recv(1024)
        print(msg.decode())
        
        client_socket.close()

if __name__ == '__main__':
    main()

## cd /cygdrive/c/Users/Brendon/Desktop/puzzle_lab/software/puzzle2
## cd /cygdrive/c/Users/Brendon/Desktop/puzzle_lab/PYTHON
## nios2-download -g puzzle2.elf
## python host.py
