import socket
import string
import random
import universitydatabasefunctions

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

    status_of_person = input("Enter your status")  # It can be either e or c. e stands for employer and c stands for candidate, later we will get it from the db

    id_of_student = input("Enter your ID : ")

    print(id_of_student)

    client_socket.send(id_of_student.encode())

    client_socket.close()
