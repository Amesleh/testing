import socket
import threading

#Define server ip and port
bind_ip = "0.0.0.0"
bind_port = 9999

#Create a socket object and bind it to the specified IP address and port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip,bind_port))

#Start listening for incoming connections, the parameter 5 is the max number of connections that the server can handle
server.listen(5)

print ("[*] Listening on %s:%d" % (bind_ip,bind_port))


# Handling incoming client connections
def handle_client(client_socket):
    request = client_socket.recv(1024)

    print ("[*] Received: %s",request)

    client_socket.send("ACK!".encode())

    client_socket.close()

while True:
    client,addr = server.accept()

    print("[*] Accepted connection from: %s:%d" % (addr[0],addr[1]))

    #handle the client's requests using the handle_client function, args passes the socket to the handle_client
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()