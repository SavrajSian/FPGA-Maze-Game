import subprocess
import socket
import time

output = subprocess.Popen("nios2-terminal", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
send_to_fpga = ""

def uart():
        output.stdin.write(bytearray(str(send_to_fpga + "\n"), 'utf-8'))                                  
        output.stdin.flush()

        val = output.stdout.readline()
        send_to_fpga = ""

        return val

def connect ():
        global connection
        try:
                client_socket.connect((server_name, server_port))
                client_socket.send("I'm an FPGA".encode())
                print("Connected")
                connection = True
                time.sleep(0.05)
        except:
                pass

def recv_msg ():
        global recv_msg
        while True:
                time.sleep(0.005)
                recv_msg = client_socket.recv(1024).decode()
                print(f"received {send_msg}")
                sender = recv_msg.split(',')[0]
                if sender == "s":
                        pass #server messages
                else: #??? messages
                        try:
                                pass    #???
                        except:
                                pass
def send_msg ():
        global send_msg
        while True:
                time.sleep(0.05)
                send_msg = uart()
                try:
                        client_socket.send(send_msg.encode())
                        print(f"sent {send_msg}")
                except:
                        pass

connection = False
server_name = '3.8.153.58'
server_port = 12000
print(f"Attempting to connect to {server_name}...")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while connection == False:
    time.sleep(0.005)
    connect()

#threading.Thread(target=send_msg).start()
#threading.Thread(target=recv_msg).start()
