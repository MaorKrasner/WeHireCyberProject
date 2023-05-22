import socket
import string
import random
import threading

from UniversityDirectory.university_database_management import *
from ChatDirectory import my_funcs

from ChatDirectory.client_chat import primes
from ChatDirectory.otp_funcs import *

seed_server = 0
user_pad = SetSeed(0,0,0)

def send_to_server_public_key_and_pq(server_socket, public_key, pq):
    server_socket.send(f'{public_key} {pq}'.encode())


def encrypt_msg(msg, pad):
    msg_bin = text_to_byte(msg)
    pad_bin = pad.my_key_stream_create_pad(len(msg_bin))  # create a pad
    enc_msg_to_send = encrypt(bytes(msg_bin, 'ascii'), bytes(pad_bin, 'ascii'))
    return enc_msg_to_send

def encrypt_file(block, pad):
    pad_bin = pad.my_key_stream_create_pad(len(block))  # create a pad
    enc_msg_to_send = encrypt(block, pad_bin.encode())
    return enc_msg_to_send


def decrypt_cipher(cipher, pad):
    pad_bin = pad.my_key_stream_create_pad(len(cipher))
    cipher_dec = decrypt(cipher, bytes(pad_bin, 'ascii'))
    msg_from_server = byte_to_text(cipher_dec)
    return msg_from_server

def decrypt_cipher_file(cipher, pad):
    pad_bin = pad.my_key_stream_create_pad(len(cipher))
    cipher_dec = decrypt(cipher, pad_bin.encode())
    return cipher_dec

def key_exchange(server_socket, p, q, x):
    y = 0
    while y == 0 or y == 1:
        if y == 1:
            p = random.choice(primes)
            q = random.choice(primes)
            x = random.randint(10, 100)
        if not my_funcs.is_prime(p) or not my_funcs.is_prime(q):
            raise ValueError('P or Q were not prime')
        eq = (p - 1) * (q - 1) + 1
        y = 1
        xy = x * y
        while xy != eq:
            x += 1
            y = eq // x
            xy = x * y


    send_to_server_public_key_and_pq(server_socket, x, p * q)  # send first time
    print("SERVER sent public and pq")

    enc_seed = int(my_funcs.receive_data_with_decode(server_socket))  # get from server the enc seed
    dec_seed = my_funcs.rsa_encryption_decryption(p * q, y, enc_seed)  # dec the enc seed
    print("SERVER RECEIVED THE DECRYPTED SEED : ")

    enc_a_b = server_socket.recv(1024).decode().split(':')
    print("SERVER RECEIVED ENC A AND B")

    enc_a = int(enc_a_b[0])
    dec_a = my_funcs.rsa_encryption_decryption(p * q, y, enc_a)
    print("SERVER ENC A : " + str(enc_a))

    enc_b = int(enc_a_b[1])
    dec_b = my_funcs.rsa_encryption_decryption(p * q, y, enc_b)
    print("SERVER ENC B : " + str(enc_b))

    return [dec_seed, int(str(dec_a) + str(dec_b)), int(str(dec_b) + str(dec_a))]

def create_random_key(n):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=n))


def candidate_func(c_socket, person_id):
    c_socket.send(encrypt_msg(f'candidate,{person_id}', user_pad))

    encrypted_response = my_funcs.receive_data(c_socket)
    if encrypted_response == "ID of student didn't show up in the database of the university!".encode():
        return "ID of student didn't show up in the database of the university!".encode()

    decrypted_file_text = decrypt_cipher(encrypted_response, user_pad)
    return decrypted_file_text

def employer_func(c_socket, person_id, content_to_verify):
    print("THE PERSON ID WE SEND : " + person_id)
    print("THE TEXT WE TRY TO SEND : " + content_to_verify)

    c_socket.send(encrypt_msg(f'employer,{person_id},{content_to_verify}', user_pad))

    encrypted_is_file_real = my_funcs.receive_data(c_socket)
    is_file_real = decrypt_cipher(encrypted_is_file_real, user_pad)
    return is_file_real


def start_client_func(data_list):
    global seed_server, user_pad

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('127.0.0.1', 2358))

    # key exchange
    seed_a_b = key_exchange(client_sock, random.choice(primes), random.choice(primes), random.randint(10, 100))
    seed_server = seed_a_b[0]
    user_pad = SetSeed(seed_a_b[0], seed_a_b[1], seed_a_b[2])  # obj that will help to generate pads for the server

    user_type = data_list[0]
    print("USER TYPE CLIENT UNI : " + user_type)

    if user_type == 'candidate':
        res = candidate_func(client_sock, data_list[1])
    else:
        res = employer_func(client_sock, data_list[1], data_list[2])

    return res