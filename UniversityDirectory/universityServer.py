import random
import socket
import string
import threading
from _thread import *
import universitydatabasefunctions

def session_with_client(client_socket, id_of_student):
    pass

if __name__ == '__main__':
    # create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind ip and port to socket
    s.bind(('192.168.0.105', 2358))  # **************************************
    # set client queue to 5
    s.listen(10)

    # server is listening all the time!!!
    while True:
        print('server is listening..')
        client_socket, address = s.accept()
        print(f'connection from {address} has been established')

        id_of_student = client_socket.recv(1024).decode()

        t1 = threading.Thread(target=session_with_client, args=(client_socket,id_of_student))
        t1.start()


