import socket
import time

def parse (msg, socket):
    global game
    if msg == "I'm the game":
        game = socket #Identify which socket is the game
        print(f"{caddr[sockets.index(game)]} is the game")
        return None, None
    elif socket != game: #from-game format ######################
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
    except:
        pass
    if received: #If received, parse
        print(f"received {recv_msg}")
        if recv_msg == "": #This signifies disconnect
            pass
            socket.close()
            sockets[sockets.index(socket)] = None #removes socket from list, keeping positions intact
            return None, None
        else:
            return parse(recv_msg, socket)
    else:
        return None, None


def send(socket, send_msg):
    try:
        socket.send(send_msg.encode())
        print(f"sent {send_msg}")
    except:
        pass

server_port = 12000
server_ip = 'localhost'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip,server_port))
server_socket.settimeout(0.01) #10ms timeout for receives, after which silent error is thrown
server_socket.listen(5) #max 4 balls + game

print('Server running on port ', server_port)

sockets = [None in range(5)]
caddr = [None in range(5)]
clients = 0
game = None

#Main server loop
while True:
    try: #keep seeing if there's new clients looking to connect
        sockets[clients], caddr[clients] = server_socket.accept()
        print(f"{caddr[clients]} connected")
        clients += 1
    except:
        pass
    for i, socket in enumerate(sockets): #send and receive linearly
        if socket:
            recipient, send_msg = recv(socket)
            if send_msg != None:
                send(recipient, send_msg)
