import socket
import time
import boto3

def parse (msg, socket):
    global game
    if msg == "I'm the game":
        socket.settimeout(0.01)
        game = socket #Identify which socket is the game
        print(f"{caddr[sockets.index(game)]} is the game")
        return None, None
    if msg == "I'm an FPGA":
        socket.settimeout(0.01)
        FPGA0 = socket #########################
        print(f"{caddr[sockets.index(FPGA0)]} is FPGA0")
        return None, None
    elif socket == game: #from-game format ######################
        print ("msg " , msg)
        recipient = msg.split(',')[0]
        print ("recipenet " ,recipient)
        slot2 = msg.split(',')[1]
        print("slot2 " ,slot2)
        score0 = (slot2.split('=')[1]).split(':')[0]
        score1 = (slot2.split('=')[1]).split(':')[1]
        score2 = (slot2.split('=')[1]).split(':')[2]
        score3 = (slot2.split('=')[1]).split(':')[3]
        score0 = int(score0)
        score1 = int(score1)
        score2 = int(score2)
        score3 = int(score3)
        print ("before appending to table")
        print ("score0, score1, score2, score3 ", score0, score1, score2, score3)
        if recipient == "s":
            if (slot2.split('=')[0] == "scores"):
                print("calling update table")
                print ("score0, score1, score2, score3 ", score0, score1, score2, score3)
                update_table("Ball 0", score0)
                update_table("Ball 1", score1)
                update_table("Ball 2", score2)
                update_table("Ball 3", score3)
            #game wants to talk to the server to update results 
            return None, None
        else:
            return recipient, msg #game to FPGA
    else: #to-game format
        return game, msg #FPGA to game
        
def update_table(Username, Score, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Scores')
    response = table.put_item(
       Item={
            'Username': Username,
            'Score': Score,
        }
    )
    return response  


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
server_ip = 'localhost'#socket.gethostbyname(socket.gethostname())#'172.31.84.206'
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
            recipient, send_msg = recv(socket)
            if send_msg != None:
                send(recipient, send_msg)