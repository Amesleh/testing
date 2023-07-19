#Some servers do not have netcat installed, but have python installed
'''
Netcat, often abbreviated as "nc," is a versatile and powerful networking utility used for reading from and writing to network connections. 
It is sometimes referred to as the "swiss army knife" of networking tools due to its wide range of capabilities.
Netcat operates both as a client and as a server and can create various types of connections over different network protocols.
'''

import sys
import socket
import getopt
import threading
import subprocess

# defining global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

#Main function:
def usage():
    print("Alghali Net Tool")
    print("")
    print("Usage: ReplacingNetcat.py -t target_host -p port")
    print("-l --listen              -listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run            execute the given file upon receiving a connection")
    print("-c --command            - initialize a command shell")
    print("-u --upload=destination          - upon receiving connection upload a file and write to [destination]")

    print("")
    print("")
    print("Examples:")
    print("ReplacingNetcat.py -t 192.168.0.1 -p 5555 -l -c")
    print("ReplacingNetcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("ReplacingNetcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print ("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    #sys.argv: a list that contains the command-line arguments passed to a script when executed, the first argument is the name of the script, and the rest represents the additional args passed to the script
    #We here have excluded the script name by starting with 1
    '''
    len(sys.argv[1:]): This gets the length (number of elements) of the list of command-line arguments passed to the script, excluding the script name.

    if not len(sys.argv[1:]): This checks if the length of the command-line arguments list is zero, meaning there are no additional arguments passed to the script.
    
    Putting it all together, the code checks if there are no command-line arguments (len(sys.argv[1:]) is zero), indicating that the script is executed without any additional arguments. In other words, it checks if the user did not provide any input when running the script.
    '''
    if not len(sys.argv[1:]):
        usage()
    '''
    This is for creating the help menu

    The getopt module allows you to define command-line options and their corresponding arguments that the script can accept.


    opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"]): This line uses the getopt.getopt() function to parse the command-line options and arguments passed to the script. The function takes two arguments:

    sys.argv[1:]: The list of command-line arguments (excluding the script name).
    "hle:t:p:cu:": The short options that the script accepts. For example, -h, -l, -e, -t, -p, -c, -u.
    ["help", "listen", "execute", "target", "port", "command", "upload"]: The long options that the script accepts. For example, --help, --listen, --execute, --target, --port, --command, --upload.

The function returns two values: opts (a list of option-value pairs) and args (a list of non-option arguments).
    '''

try:
    opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",
    ["help","listen","execute","target","port","command","upload"])
except getopt.GetoptError as err:
    print (err)
    usage()

for o,a in opts:
    if o in ("-h","--help"):
        usage()
    elif o in ("-l","--listen"):
        listen = True
    elif o in ("-e", "--execite"):
        execute = a
    elif o in ("-c", "--commandshell"):
        command = True
    elif o in ("-u", "--upload"):
        upload_destination = a
    elif o in ("-t","--target"):
        target = a
    elif o in ("-p","--port"):
        port = int(a)
    else:
        assert False,"Unhandled Option idiot"


# choosing if to listen to send data from stdin
'''
we are trying to mimic
netcat to read data from stdin and send it across the network. As noted, if
you plan on sending data interactively, you need to send a ctrl-D to bypass
the stdin read. 
'''
if not listen and len(target) and port>0:

    #read in the buffer from the commandline
    #this will bolck, send using CTRL-D if not sending input to stdin
    buffer = sys.stdin.read()

    #sending data:
    client_sender(buffer)


#we are going to listen and upload, execute and drop a shell back
#this all depends on the cl options



if listen:
    '''
    is where we detect that we are to set up
    a listening socket and process further commands (upload a file, execute a
    command, start a command shell).
    '''
    server_loop()

main()

def client_sender(buffer):
    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #connecting:
        client.connect((target,port))

        '''
        We start by set-
    ting up our TCP socket object and then test u to see if we have received
    any input from stdin. If all is well, we ship the data off to the remote target
    and receive back data
        '''
        if len(buffer):
            client.send(buffer)

        '''
        until there is no more data to receive. We then wait
    for further input from the user, and continue sending and receiving data
    until the user kills the script. The extra line break is attached specifically
    to our user input so that our client will be compatible with our command
    shell. Now we’ll move on and create our primary server loop and a stub
    function that will handle both our command execution and our full com-
    mand shell.
        '''
        while True:
            # now wait for data back:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response+= data

                if recv_len<4096:
                    break

            print (response),
            #waiting for more input
            buffer = raw_input("")
            buffer+= "\n"

            #sending it
            client.send(buffer)

    except:
        print("[*] Exiting")
        client.close()

def server_loop():
    global target

    #if no target is defined, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()


def run_command(command):
        #trim the newline,  rstrip() method is a string method used to remove trailing whitespace characters (spaces, tabs, newlines, etc.)
        command = command.rstrip()

        #run the command and get the output back
        try:
            output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
        except:
            output = "Failed"
        
        return output
        
    
        '''
        subprocess provides a powerful process-creation interface
    that gives you a number of ways to start and interact with client programs.
        in this case u, we’re simply running whatever command we pass in, run-
    ning it on the local operating system, and returning the output from
    the command back to the client that is connected to us.
        '''


#logic for uploads, command execution and shell:
def client_handler(client_socket):
    global upload
    global execute
    global command


    #checking for upload
    if len(upload_destination):

        #read in all of the bytes and write to our destination
        file_buffer = ""

        #keep reading data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data
            
            #taking the bytes an writing them out:
            try:
                file_descriptor = open(upload_destination, "wb") #wb is used for writing binary data to the file
                file_descriptor.write(file_buffer)
                file_descriptor.close()

                #confirm that we wrote the file out:
                client_socket.send("Successfully saved the file to %s\r\n" %upload_destination)
            except:
                client_socket.send("Failed to save to file")

            #check for command execution
            if len(execute):
                output = run_command(execute)
                client_socket.send(output)
            if command:
                while True:
                    client_socket.send("alghali")
                    cmd_buffer = ""
                    while "\n" not in cmd_buffer:
                        cmd_buffer += client_socket.recv(1024)

                    response = run_command(cmd_buffer)
                    client_socket.send(response)