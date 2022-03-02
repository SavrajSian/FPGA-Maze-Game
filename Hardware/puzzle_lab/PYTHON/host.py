import subprocess

def send_on_jtag(cmd):
    assert (cmd == 'n' or cmd == 'f')

    output = subprocess.Popen("nios2-terminal", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    output.stdin.write(bytearray(str(cmd + "\n"), 'utf-8'))
    output.stdin.flush()

def perform_computation():
    cmd = input()
    res = send_on_jtag(cmd)

def main():
    perform_computation()
    
if __name__ == '__main__':
    main()
