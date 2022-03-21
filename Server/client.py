import subprocess
import socket
import time
import threading

output = subprocess.Popen("nios2-terminal", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
for i in range(5):
	val = output.stdout.readline() #get rid of header from nios2-terminal
send_to_fpga = "!"
reset_7seg = 0

ID = None
switch = '0'

def UART():
	global send_to_fpga, reset_7seg
	output.stdin.write(bytearray(str(send_to_fpga + "\n"), 'utf-8'))
	output.stdin.flush()
	if send_to_fpga != "!":
		print(send_to_fpga)
	send_to_fpga = "!"
	val = output.stdout.readline().decode()
	return val

def connect ():
	global connection
	try:
		client_socket.connect((server_name, server_port))
		time.sleep(0.05)
		connection = True
	except:
		pass
	try:
		client_socket.send("~I'm an FPGA".encode())
		print("Connected")
		time.sleep(0.05)
	except:
		pass

def recv_msg ():
	global recv_msg, ID, send_to_fpga
	while True:
		time.sleep(0.005)
		recv_msg = client_socket.recv(1024).decode()
		print(f"received {recv_msg}")
		if "~You are FPGA" in recv_msg: #assignment
			ID = int(recv_msg[-1])
			print(f"~I am FPGA{ID}")
			SEG_IDs = ["s", "y", "g", "b"]
			send_to_fpga = SEG_IDs[ID]
		else:   
			sender = recv_msg.split(',')[0]
			if sender == "~s":
				if "7SEG=" in recv_msg:
					send_to_fpga = recv_msg.split('=')[1].split('~')[0][0]
			else: #from game
				if "LIFE-" in recv_msg:
					send_to_fpga = "l"

def send_msg ():
	global send_msg, switch
	i = 0
	while True:
		i += 1
		msg = UART()
		if i % 10 == 0: #infrequent sends
			time.sleep(0.005)
			send_msg = f"~{ID}," + msg.split()[0] + ":" + msg.split()[1] + ","
			if msg.split()[3] != "3":
				send_msg += "buttonpress,"
			if msg.split()[2] != switch:
				send_msg += f"switch={msg.split()[2]},"
				switch = msg.split()[2]
			try:
				client_socket.send(send_msg.encode())
				print(f"sent {send_msg}")
			except:
				pass

connection = False
server_name = '3.85.233.169' #"192.168.56.1"
server_port = 12000
print(f"Attempting to connect to {server_name}...")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while connection == False:
	time.sleep(0.005)
	connect()

threading.Thread(target=send_msg).start()
threading.Thread(target=recv_msg).start()