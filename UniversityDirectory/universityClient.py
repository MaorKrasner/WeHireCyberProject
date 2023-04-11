import os
import socket
import string
import random
from universitydatabasefunctions import *
from my_funcs import *

PORT_NUMBER = 2358


def create_random_key(n):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=n))


if __name__ == '__main__':
    # TODO : SEPERATE CASES OF STUDENT AND EMPLOYER
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(("127.0.0.1", 2358))
    except socket.error as e:
        print(str(e))
    print("Connected to server")

    status_of_person = input("Enter e if you are an employer, Enter c if you are candidate : ")
    while status_of_person != "c" and status_of_person != "e":
        status_of_person = input("Enter e if you are an employer, Enter c if you are candidate : ")

    client_socket.send(status_of_person.encode())
    answer = client_socket.recv(1024).decode()
    print(answer)

    if status_of_person == "c":
        id_of_candidate = input("Enter your ID : ")
        key_to_sign_file_with = create_random_key(random.randint(16, 128))
        print("Key is : " + key_to_sign_file_with)
        client_socket.send((id_of_candidate + " " + key_to_sign_file_with).encode())

        signed_file_content = recvall_with_decode(client_socket)
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        full_diploma_path = desktop_path + "/" + find_signed_file_name(id_of_candidate)
        print(full_diploma_path)
        file = open(full_diploma_path, 'a')
        file.write(signed_file_content)
        file.close()
        print("I saved for you the file in : " + desktop_path)
    client_socket.close()
