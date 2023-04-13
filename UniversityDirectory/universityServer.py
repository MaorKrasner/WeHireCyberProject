import os.path
import pathlib
import random
import socket
import string
import threading
from _thread import *
from universitydatabasefunctions import *
from my_funcs import *


def session_with_client(sock):
    status_of_person = sock.recv(1024).decode()
    message_back = "The server received a request from "
    addition_to_send = "a candidate" if status_of_person == "c" else "an employer"
    message_back += addition_to_send
    sock.send(message_back.encode())

    if status_of_person == "c":
        info_list = client_socket.recv(1024).decode().split(" ")
        id_of_candidate, key_to_sign_diploma = info_list[0], info_list[1]
        status, message = create_diploma_and_sign_it(id_of_candidate, key_to_sign_diploma)

        print("status is : " + str(status))

        if status is True:
            sock.send(message)
        else:
            sock.send("ID of student didn't show up in the database of the university!".encode())
    else:
        id_of_candidate = sock.recv(1024).decode()
        sock.send(("Server Received id : " + id_of_candidate).encode())
        binary_file_to_check_content = recvall_without_decode(sock)
        status = verify_if_the_certificate_is_real(id_of_candidate, binary_file_to_check_content)
        if status:
            sock.send("The student's diploma is real".encode())
        else:
            sock.send(
                "The student changed his diploma/The ID of student didn't show up in the database of the university!".encode())


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

        t1 = threading.Thread(target=session_with_client, args=client_socket)
        t1.start()
