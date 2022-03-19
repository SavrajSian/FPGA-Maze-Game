import socket
import time

def parse (msg, socket):
    global game
    if msg == "~I'm the game":
        socket.settimeout(0.01)
        game = socket #Identify which socket is the game
        print(f"{caddr[sockets.index(game)]} is the game")
        return None, None
    if msg == "~I'm an FPGA":
        socket.settimeout(0.01)
        FPGAs.append(socket)
        print(f"{caddr[sockets.index(FPGAs[-1])]} is FPGA{len(FPGAs)-1}") #e.g. "172.31.84.206" is FPGA0
        send(game, f"~FPGA{len(FPGAs)-1} connected") #Send notification to game as well (game must start first)
        return socket, f"~You are FPGA{len(FPGAs)-1}" #Send to FPGA to assign identity
    elif socket == game: #from-game format ######################
        recipient = msg.split(',')[0]
        if recipient == "s":
            #TODO: game wants to talk to server only
            return None, None
        else:
            return recipient, msg #game to FPGA
    else: #to-game format
        return game, msg #FPGA to game
        

def recv(socket):
    received = False
    try:
        recv_msg = socket.recv(1024).decode()
        received = True
    except: #This signifies disconnect
        if socket != game:
            FPGA_empties[FPGAs.index(socket)] += 1 #No message received; suspicious
            if FPGA_empties[FPGAs.index(socket)] % 30 == 0: #At least 10 empties received (doesn't need reset)
                print(f"FPGA{FPGAs.index(socket)} disconnected")
                send(game, f"~FPGA{FPGAs.index(socket)} disconnected")
                FPGAs.remove(socket)
                socket.close() #Attempt graceful disconnect
                sockets[sockets.index(socket)] = None #removes socket from list, keeping positions intact
                if FPGAs == []:
                    quit() #if last FPGA disconnects, end the server process

        pass
    if received: #If received, parse
        try:
            if socket != game:
                FPGA_empties[FPGAs.index(socket)] = 0 #reset empties
        except: 
            pass
        if recv_msg != "":
            print(f"received {recv_msg}")
            recipient, send_msg = parse(recv_msg, socket)
            send(recipient, send_msg)
    else:
        pass


def send(socket, send_msg):
    try:
        socket.send(send_msg.encode())
        print(f"sent {send_msg}")
    except:
        pass

server_port = 12000
server_ip = socket.gethostbyname(socket.gethostname())#'172.31.84.206'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip,server_port))
server_socket.settimeout(0.01) #10ms timeout for receives, after which silent error is thrown
server_socket.listen(5) #max 4 balls + game

print('Server running on port ', server_port)

sockets = [None, None, None, None, None]
#socket_empties [None in range(5)]
caddr = [None, None, None, None, None]
clients = 0
game = None
FPGAs = []
FPGA_empties = [0, 0, 0, 0] #Counts how many times "" is received (suggests disconnect)

#Main server loop
while True:
    try: #keep seeing if there's new clients looking to connect
        sockets[clients], caddr[clients] = server_socket.accept()
        print(f"{caddr[clients]} connected")
        clients += 1
    except:
        pass
    for i, socket in enumerate(sockets): #send and receive linearly
        if socket != None:
            recv(socket) #receive, and then perhaps send
