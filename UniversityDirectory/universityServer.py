import os.path
import pathlib
import random
import socket
import string
import threading
from _thread import *
from universitydatabasefunctions import *


def session_with_client(client_socket, id_of_student):
    pass


if __name__ == '__main__':
    # create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind ip and port to socket
    s.bind(('0.0.0.0', 2358))  # **************************************
    # set client queue to 5
    s.listen(10)

    # server is listening all the time!!!
    while True:
        print('server is listening..')
        client_socket, address = s.accept()
        print(f'connection from {address} has been established')

        status_of_person = client_socket.recv(1024).decode()
        message_back = "The server received a request from "
        addition_to_send = "a candidate" if status_of_person == "c" else "an employer"
        message_back += addition_to_send
        client_socket.send(message_back.encode())

        if status_of_person == "c":
            info_list = client_socket.recv(1024).decode().split(" ")
            id_of_candidate, key_to_sign_diploma = info_list[0], info_list[1]
            status, message = create_diploma_and_sign_it(id_of_candidate, key_to_sign_diploma) #prob here

            if status is True:
                client_socket.send(message.encode())

        # t1 = threading.Thread(target=session_with_client, args=(client_socket,id_of_student))
        # t1.start()
