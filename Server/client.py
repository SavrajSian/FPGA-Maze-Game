import subprocess
import socket
import time
import threading

output = subprocess.Popen("nios2-terminal", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
for i in range(4):
	val = output.stdout.readline().decode() #get rid of header from nios2-terminal
send_to_fpga = ""
ID = None
switch = '0'

def UART():
	global send_to_fpga
	#output.stdin.write(bytearray(str(send_to_fpga + "\n"), 'utf-8'))                                  
	#output.stdin.flush()
	val = output.stdout.readline().decode()
	send_to_fpga = ""
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
	except Exception as e:
		print(e)
		pass

def recv_msg ():
	global recv_msg, ID
	while True:
		time.sleep(0.005)
		recv_msg = client_socket.recv(1024).decode()
		print(f"received {recv_msg}")
		if "~You are FPGA" in recv_msg: #assignment
			ID = int(recv_msg[-1])
			print(f"~I am FPGA{ID}")
		else:   
			sender = recv_msg.split(',')[0]
			if sender == "s":
				pass #server messages
			else: #??? messages
				try:
					pass    #???
				except:
					pass

def send_msg ():
	global send_msg, switch
	i = 0
	while True:
		i += 1
		msg = UART()
		if i % 100 == 0: #infrequent sends
			send_msg = f"~{ID}," + msg.split()[0] + ":" + msg.split()[1] + ","
			if msg.split()[3] != "3":
				send_msg += "buttonpress,"
			if msg.split()[2] != switch:
				send_msg += f"switch={msg.split()[2]},"
				switch = msg.split()[2]
			time.sleep(0.05)
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