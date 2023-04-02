import socket
import os
from _thread import *

PORT_NUMBER = 55555


if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(("0.0.0.0", PORT_NUMBER))
    except socket.error as e:
        print(str(e))
    print('Server is up and running. Waiting for connection response')

    server_socket.listen()
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")

    data = client_socket.recv(1024).decode()
    print("Client sent : " + data)

    reply = "Hello " + data

    client_socket.send(reply.encode())

    client_socket.close()
    server_socket.close()


