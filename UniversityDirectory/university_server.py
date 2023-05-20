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
    print("CLIENT RECEIVED PUBLIC AND PQ")
    public_pq = [int(i) for i in public_key_and_pq.split(' ')]  # first public key second pq
    print("CLIENT PUBLIC KEY : " + str(public_pq[0]))
    print("CLIENT PQ : " + str(public_pq[1]))

    # create the seed randomly and send it to the client
    seed = random.randint(0, 5000)
    print("CLIENT SEED : " + str(seed))
    a = random.randint(10, 99)
    print("CLIENT A : " + str(a))
    abseed.append(a)
    b = random.randint(10, 99)
    print("CLIENT B : " + str(b))
    abseed.append(b)
    abseed.append(seed)

    public_pq.append(seed)  # third seed
    enc_seed = my_funcs.rsa_encryption_decryption(public_pq[1], public_pq[0], public_pq[2])     # encrypt the seed

    client_socket.send(str(enc_seed).encode())  # send the enc seed to the client
    print("CLIENT SENT ENC SEED")

    enc_a = my_funcs.rsa_encryption_decryption(public_pq[1], public_pq[0], abseed[0])
    enc_b = my_funcs.rsa_encryption_decryption(public_pq[1], public_pq[0], abseed[1])

    client_socket.send(f'{enc_a}:{enc_b}'.encode())
    print("CLIENT SENT ENC A AND B")

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



def session_with_client_uni(sock):
    ab_seed = key_exchange(sock)
    pad = SetSeed(ab_seed[2], ab_seed[0], ab_seed[1])

    encrypted_user_type = my_funcs.receive_data(sock)
    user_type_and_others = decrypt_cipher(encrypted_user_type, pad).split(',')  # all the data that is passed through the socket

    print("TYPE : " + user_type_and_others[0])

    #candidate section
    if user_type_and_others[0] == 'candidate':
        print("I'M IN UNI FUNC!")
        person_id = user_type_and_others[1]
        print("PERSON ID TO SIGN: " + person_id)
        signing_key = create_random_key(random.randint(32, 128))
        print("SIGNING KEY : " + ''.join(signing_key))

        status, message = create_and_sign_diploma(person_id, signing_key)
        print("STATUS : " + str(status))

        if status:
            sock.send(encrypt_msg(message, pad))
        else:
            sock.send("ID of student didn't show up in the database of the university!".encode())

    # employer section
    else:
        person_id, content_to_verify = user_type_and_others[1], user_type_and_others[2]
        print("PERSON ID TO VERIFY: " + person_id)
        print("CONTENT TO VERIFY : " + content_to_verify)

        status_of_verification = verify_integrity_of_certificate(person_id, content_to_verify.encode())
        sock.send(encrypt_msg(str(status_of_verification), pad))



if __name__ == '__main__':
    # create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind ip and port to socket
    s.bind(('0.0.0.0', 2358))  # **************************************
    # set client queue to 5
    s.listen(20)

    # server is listening all the time!!!
    while True:
        print('server is listening..')
        client_socket, address = s.accept()
        print(f'connection from {address} has been established')

        session_with_client_uni(client_socket)