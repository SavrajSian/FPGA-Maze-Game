import subprocess
import socket

def send_on_jtag(msg):
    #assert len(msg)>=1, "Please make the cmd a single character"

    output = subprocess.Popen("nios2-terminal", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    #output.stdin.write(bytearray(str(cmd + "\n"), 'utf-8'))
    #output.stdin.flush()

    vals = output.stdout.readlines() 

    return vals[4]

server_name = 'localhost'
server_port = 12000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(0.01) #10ms timeout for receives, after which silent error is thrown
connection = False
send_msg = "0,33333333:33333333,"

def network():
    global recv_msg, send_msg, connection
    if connection == False:
            try:
                    try: client_socket.connect((server_name, server_port))
                    except: pass
                    client_socket.send("I'm an FPGA".encode())
                    print("Connected")
                    connection = True
            except:
                    pass
    else: #connected
            received = False
            try:
                    recv_msg = client_socket.recv(1024).decode()
                    print(f"received {send_msg}")
                    received = True
            except:
                    pass
            if received:
                    sender = recv_msg.split(',')[0]
                    if sender == "s":
                            pass #server messages
                    else: #??? messages
                            try:
                                    #???
                            except:
                                    pass
                    try:
                            client_socket.send(send_msg.encode())
                            print(f"sent {send_msg}")
                    except:
                            pass
            send_msg_prev = send_msg

while True:
    network()

