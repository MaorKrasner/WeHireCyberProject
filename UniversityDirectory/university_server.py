import random
import socket
import string
import threading
from university_database_management import *
from ChatDirectory import my_funcs
from ChatDirectory.otp_funcs import *


def key_exchange(client_socket):
    abseed = []
    public_key_and_pq = my_funcs.receive_data_with_decode(client_socket)  # get the public key and the pq
    public_pq = [int(i) for i in public_key_and_pq.split(' ')]  # first public key second pq

    # create the seed randomly and send it to the client
    seed = random.randint(0, 5000)
    a = random.randint(10, 99)
    abseed.append(a)
    b = random.randint(10, 99)
    abseed.append(b)
    abseed.append(seed)

    public_pq.append(seed)  # third seed
    enc_seed = my_funcs.rsa_encryption_decryption(public_pq[1], public_pq[0], public_pq[2])     # encrypt the seed

    client_socket.send(str(enc_seed).encode())  # send the enc seed to the client

    enc_a = my_funcs.rsa_encryption_decryption(public_pq[1], public_pq[0], ab[0])
    client_socket.send(str(enc_a).encode())

    enc_b = my_funcs.rsa_encryption_decryption(public_pq[1], public_pq[0], ab[1])
    client_socket.send(str(enc_b).encode())

    abseed[0] = int(str(a) + str(b))
    abseed[1] = int(str(b) + str(a))

    return abseed

def encrypt_msg(msg, pad):
    msg_bin = text_to_byte(msg)
    pad_bin = pad.my_key_stream_create_pad(len(msg_bin))  # create a pad
    enc_msg_to_send = encrypt(bytes(msg_bin, 'ascii'), bytes(pad_bin, 'ascii'))
    return enc_msg_to_send


def encrypt_msg_file(block, pad):
    pad_bin = pad.my_key_stream_create_pad(len(block))  # create a pad
    enc_msg_to_send = encrypt(block, pad_bin.encode())
    return enc_msg_to_send


def decrypt_cipher(cipher, pad):
    pad_bin = pad.my_key_stream_create_pad(len(cipher))
    cipher_dec = decrypt(cipher, bytes(pad_bin, 'ascii'))
    msg_from_client = byte_to_text(cipher_dec)
    return msg_from_client


def decrypt_cipher_file(cipher, pad):
    pad_bin = pad.my_key_stream_create_pad(len(cipher))
    cipher_dec = decrypt(cipher, pad_bin.encode())
    return cipher_dec


def create_random_key(n):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=n))



def session_with_client(sock):
    ab_seed = key_exchange(sock)
    pad = SetSeed(ab_seed[2], ab_seed[0], ab_seed[1])

    encrypted_user_type = my_funcs.receive_data(sock)
    user_type = decrypt_cipher(encrypted_user_type, pad)

    #candidate section
    if user_type == 'candidate':
        encrypted_person_id = my_funcs.receive_data(sock)
        person_id = decrypt_cipher(encrypted_person_id, pad)
        signing_key = create_random_key(random.randint(32, 128))

        status, message = create_and_sign_diploma(person_id, signing_key)

        if status:
            pass
        else:
            sock.send("ID of student didn't show up in the database of the university!".encode())

    # employer section
    else:
        pass

    status_of_person = sock.recv(1024).decode()
    message_back = "The server received a request from "
    addition_to_send = "a candidate" if status_of_person == "c" else "an employer"
    message_back += addition_to_send
    sock.send(message_back.encode())

    if status_of_person == "c":
        info_list = client_socket.recv(1024).decode().split(" ")
        id_of_candidate, key_to_sign_diploma = info_list[0], info_list[1]
        status, message = create_and_sign_diploma(id_of_candidate, key_to_sign_diploma)
        #status, message = create_diploma_and_sign_it(id_of_candidate, key_to_sign_diploma)

        print("status is : " + str(status))

        if status is True:
            sock.send(message)
        else:
            sock.send("ID of student didn't show up in the database of the university!".encode())
    else:
        id_of_candidate = sock.recv(1024).decode()
        sock.send(("Server Received id : " + id_of_candidate).encode())
        binary_file_to_check_content = my_funcs.receive_data(sock)
        status = verify_integrity_of_certificate(id_of_candidate, binary_file_to_check_content)
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

        t1 = threading.Thread(target=session_with_client, args=(client_socket,))
        t1.start()
