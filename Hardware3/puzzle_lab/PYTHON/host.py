import subprocess
from time import sleep
import socket

output = subprocess.Popen("nios2-terminal", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)


def send_on_jtag(cmd):
    output.stdin.write(bytearray(str(cmd + "\n"), 'utf-8'))
    try:output.stdin.flush()
    except Exception as e:
        print(e)
        pass
    val = output.stdout.readline()
    return val

def perform_computation():
    res = send_on_jtag("s")
    return res

def perform_computation2():
    res = send_on_jtag("y")
    return res

def perform_computation3():
    res = send_on_jtag("1")
    return res

def perform_computation4():
    res = send_on_jtag("!")
    return res

def perform_computation5():
    res = send_on_jtag("l")
    return res

def perform_computation6():
    res = send_on_jtag("g")
    return res

def main():
    print("We're in tcp client..."); 
    #the server name and port client wishes to access 
    server_name = '3.8.153.58' # FIXME: Put your server ipv4 addr
    #'52.205.252.164' 
    server_port = 12000

    send_msg = "Connecting to server!"
    
    # for i in range(400):
    #     msg = perform_computation()
    #     print(msg)
    
    # for i in range(400):
    #     msg = perform_computation2()
    #     print(msg)

    # for i in range(400):
    #     msg = perform_computation3()
    #     print(msg)

    msg = perform_computation()     # SEND FIRST MESSAGE ONCE
    print(msg)

    for i in range(400):
        msg = perform_computation4()    # SEND EMPTY TEXT 400 TIMES
        print(msg)
    
    msg = perform_computation2()    # SEND SECOND MESSAGE ONCE
    print(msg)

    for i in range(400):
        msg = perform_computation4()    # SEND EMPTY TEXT 400 TIMES
        print(msg)

    msg = perform_computation5()    # REDUCE LIFE
    print(msg)
    msg = perform_computation5()    # REDUCE LIFE
    print(msg)
    msg = perform_computation5()    # REDUCE LIFE
    print(msg)
    msg = perform_computation5()    # REDUCE LIFE
    print(msg)
    msg = perform_computation5()    # REDUCE LIFE
    print(msg)

    msg = perform_computation3()    # SEND THIRD MESSAGE ONCE
    print(msg)

    for i in range(400):
        msg = perform_computation4()    # SEND EMPTY TEXT 400 TIMES
        print(msg)

    msg = perform_computation6()    # INCREASE LIFE
    print(msg)
    msg = perform_computation6()    # INCREASE LIFE
    print(msg)

    while(1):
        #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #client_socket.connect((server_name, server_port))
        #some work
    
        msg = perform_computation4()
        print(msg)

        #msg = perform_computation3()
        #print(msg)
        #send the message  to the udp server
        #client_socket.send(msg)

        #return values from the server
        #msg = client_socket.recv(1024)
        #print(msg.decode())

        #send_msg = msg
        
        #client_socket.close()


if __name__ == '__main__':
    main()

## cd /cygdrive/c/Users/Brendon/Desktop/puzzle_lab/software/puzzle2
## cd /cygdrive/c/Users/Brendon/Desktop/puzzle_lab/PYTHON
## nios2-download -g puzzle2.elf
## python host.py


## cd /cygdrive/c/Users/Brendon/Desktop/puzzle_lab/software/puzzle2
## cd /cygdrive/c/Users/Brendon/Desktop/puzzle_lab/PYTHON
## nios2-download -g puzzle2.elf
## python host.py


# cd /cygdrive/c/Users/Brendon/Documents/Github/Info_Proc_Lab/Server

		# 	//print(0, 0, 0, 0, 0, 0);
		# 	// Text needs to be of multiple of 6. For now add spaces?
		# 	// W = VV
		# 	// M = nn

		# /*print(getBin(to_print[0]), getBin(to_print[1]), getBin(to_print[2]), getBin(to_print[3]), getBin(to_print[4]), getBin(to_print[5]));
		# if (length != 0)
		# {
		# 	rotation = 0;
		# }
		# else
		# {
		# 	if (rotation = 19) { print(0, 0, 0, 0, 0, 0); }
		# 	else
		# 	{

		# 	}
		# }
		# if ( (length == 0) && (rotation = 19) ) { print(0, 0, 0, 0, 0, 0); }
		# else
		# {
		# 	if (length == 0)
		# 	{
		# 		if (count == 100){
		# 			print(getBin(hold_data[rotation%6]), getBin(hold_data[(rotation+1)%6]), getBin(hold_data[(rotation+2)%6]), getBin(hold_data[(rotation+3)%6]), getBin(hold_data[(rotation+4)%6]), getBin(hold_data[(rotation+5)%6]));
		# 			rotation += 1;
		# 			count = 0;
		# 		}
		# 	}
		# }*/