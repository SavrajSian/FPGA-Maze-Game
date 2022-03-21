import socket
import time
import LoadScores, UpdateScores
import LoadKills, UpdateKills

def parse (msg, socket):
	global game
	if msg == "~I'm the game":
		socket.settimeout(0.01)
		game = socket #Identify which socket is the game
		print(f"{caddr[sockets.index(game)]} is the game")
	if msg == "~I'm an FPGA":
		socket.settimeout(0.01)
		FPGAs.append(socket)
		print(f"{caddr[sockets.index(FPGAs[-1])]} is FPGA{len(FPGAs)-1}") #e.g. "172.31.84.206" is FPGA0
		send(game, f"~FPGA{len(FPGAs)-1} connected") #Send notification to game as well (game must start first)
		send(socket, f"~You are FPGA{len(FPGAs)-1}") #Send to FPGA to assign identity
	elif socket == game: #from-game format
		recipient = msg.split(',')[0]
		if recipient == "~s": 			#game wants to talk to server only
			if "scores" in msg:
				scores = [int(msg.split('=')[1].split(":")[i]) for i in range(4)]	
				UpdateScores.upload_scores(scores)
				high_scores = LoadScores.get_scores()
				for i in range(len(high_scores)):
					for j in range(len(high_scores[i])):
						high_scores[i][j] = str(high_scores[i][j])
					high_scores[i] = ";".join(high_scores[i])
				high_scores = "|".join(high_scores)
				msg = "~s,high_scores=" + high_scores
				sort_order = []
				for i in range(len(scores)):
					sort_order.append([i, scores[i]])
				sort_order = sorted(sort_order, key=lambda x: x[1], reverse=True)
				try:
					first = FPGAs[int(sort_order[0][0])]
					send(first, "~s,7SEG=1ST")
				except: pass
				try:
					second = FPGAs[int(sort_order[1][0])]
					send(second, "~s,7SEG=2ND")
				except: pass
				try:
					third = FPGAs[int(sort_order[2][0])]
					send(third, "~s,7SEG=3RD")
				except: pass
				try:
					fourth = FPGAs[int(sort_order[3][0])]
					send(fourth, "~s,7SEG=4TH")
				except: pass
			elif "kills" in msg:
				kills = [int(msg.split('=')[1].split(":")[i]) for i in range(4)]
				UpdateKills.upload_kills(kills)
				high_kills = LoadKills.get_kills()
				for i in range(len(high_kills)):
					for j in range(len(high_kills[i])):
						high_kills[i][j] = str(high_kills[i][j])
					high_kills[i] = ";".join(high_kills[i])
				high_kills = "|".join(high_kills)
				msg = "~s,high_kills=" + high_kills
			send(game, msg)
		else:
			try:  #game to FPGA
				FPGA = FPGAs[int(recipient[1:])]
				send(FPGA, msg)
			except: pass
	else: #to-game format
		send(game, msg) #FPGA to game
		

def recv(socket):
	received = False
	try:
		recv_msg = socket.recv(1024).decode()
		received = True
	except: #This signifies disconnect
		if socket != game:
			FPGA_empties[FPGAs.index(socket)] += 1 #No message received; suspicious
			if FPGA_empties[FPGAs.index(socket)] > 500: #At least 500 empties received
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
			parse(recv_msg, socket)
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
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
