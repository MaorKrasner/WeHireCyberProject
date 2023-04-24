import random
import socket
import threading
import time

from ChatDirectory import my_funcs
from ChatDirectory.otp_funcs import *
from client_start_gui import *
#from client_login_gui import *
#from client_create_account_gui import *
from candidate_gui import *
import hashlib
import hmac
import pickle
import imutils
import struct
import cv2
import sys

data_list = []  # index0 = pq, index1 = public key, index2 = private key
data_list_for_private = []  # index0 = pq, index1 = public key, index2 = private key, index3 = pad**OR**index0 = pq, index1 = public key, index2 = pad
private_flag = False
# primes = [i for i in range(4000, 8999) if my_funcs.is_prime(i)]
primes = [i for i in range(100, 999) if my_funcs.is_prime(i)]

user_pad = SetSeed(0, 0, 0)  # !!!!!

s = 0  # server socket
user_name = None
seed_server = 0
hmac_flag_txt = False
hmac_flag_photo = False
hack_flag = False


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

    data_list.append(p * q)
    data_list.append(x)
    data_list.append(y)
    print("public key, x: " + str(x))
    print("private key, y: " + str(y))
    print("modulo (pq): " + str(p * q))

    send_to_server_public_key_and_pq(server_socket, x, p * q)  # send first time

    enc_seed = int(my_funcs.receive_data_with_decode(server_socket))  # get from server the enc seed
    print(f'enc seed    {enc_seed}')
    dec_seed = my_funcs.rsa_encryption_decryption(p * q, y, enc_seed)  # dec the enc seed
    print(f'seed    {dec_seed}')

    enc_a = server_socket.recv(32).decode()
    print(f'1 {enc_a}')

    if not enc_a.isdigit():
        sys.exit()

    enc_b = server_socket.recv(32).decode()
    print(f'2 {enc_b}')

    enc_a = int(enc_a)
    print(f'enc a2    {enc_a}')
    dec_a = my_funcs.rsa_encryption_decryption(p * q, y, enc_a)
    print(f'a    {dec_a}')


    enc_b = int(enc_b)
    print(f'enc b    {enc_b}')
    dec_b = my_funcs.rsa_encryption_decryption(p * q, y, enc_b)
    print(f'b    {dec_b}')



    return [dec_seed, int(str(dec_a) + str(dec_b)), int(str(dec_b) + str(dec_a))]


def key_exchange_for_private(server_socket, p, q, x):
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

    data_list_for_private.append(p * q)
    data_list_for_private.append(x)
    data_list_for_private.append(y)
    print("public key_for_private, x: " + str(x))
    print("private key_for_private, y: " + str(y))
    print("modulo_for_private (pq): " + str(p * q))

    print('*')

    send_to_server_public_key_and_pq_for_private(server_socket, x, p * q)

    print('**')

    enc_seed = int(my_funcs.receive_data_with_decode(server_socket))
    print('***')
    print(f'enc seed_for_private1    {enc_seed}')
    dec_seed = my_funcs.rsa_encryption_decryption(p * q, y, enc_seed)
    print(f'seed_for_private    {dec_seed}')

    data_list_for_private.append(SetSeed(dec_seed, 8888, 9999))


def send_to_server_public_key_and_pq_for_private(server_socket, public_key, pq):
    server_socket.send(f'{public_key}'.encode())
    time.sleep(0.05)
    print('$')
    server_socket.send(f'{pq}'.encode())
    print('$$')


def send_to_server_public_key_and_pq(server_socket, public_key, pq):
    server_socket.send(f'{public_key} {pq}'.encode())


def recive_ongoing_msg_from_chat_server(s, pad):
    global private_flag
    while True:
        if not private_flag:
            enc_msg_from_server = my_funcs.receive_data(s)
            msg_from_server = decrypt_cipher(enc_msg_from_server, pad)

            if msg_from_server == "kill yourself":
                s.close()
                break

            if msg_from_server == "creator_rsa":
                key_exchange_for_private(s, random.choice(primes), random.choice(primes),
                                         random.randint(10, 100))  # ***
                private_flag = True

            if msg_from_server == 'second_participant':
                public_key = int(my_funcs.receive_data_with_decode(s))
                qp = int(my_funcs.receive_data_with_decode(s))
                data_list_for_private.append(qp)
                data_list_for_private.append(public_key)
                seed = random.randint(0, 500)
                print(f'seed_for_private2    {seed}')
                data_list_for_private.append(SetSeed(seed, 8888, 9999))
                enc_seed = my_funcs.rsa_encryption_decryption(qp, public_key, seed)
                print(f'enc seed_for_private2    {enc_seed}')
                s.send(str(enc_seed).encode())
                private_flag = True

            print(msg_from_server)
        else:
            enc_private_msg_from_server = my_funcs.receive_data(s)
            if enc_private_msg_from_server == '1'.encode():
                s.send('stam'.encode())
                private_flag = False
                data_list_for_private.clear()
                print('exit from private session')
            else:
                if private_flag:
                    private_msg_from_server = decrypt_cipher(enc_private_msg_from_server, data_list_for_private[-1])
                    print(private_msg_from_server)


def encrypt_msg(msg, pad):
    msg_bin = text_to_byte(msg)
    pad_bin = pad.my_key_stream_create_pad(len(msg_bin))  # create a pad
    # print(f'encryption pad for {msg}:\n{bytes(pad_bin, "ascii")}')

    enc_msg_to_send = encrypt(bytes(msg_bin, 'ascii'), bytes(pad_bin, 'ascii'))
    # print(f'enc msg: {enc_msg_to_send}')

    # dec_msg = decrypt(enc_msg_to_send, bytes(pad_bin, 'ascii'))
    # print(f'************: {byte_to_text(dec_user_name)}')
    return enc_msg_to_send

def encrypt_file(block, pad):
    pad_bin = pad.my_key_stream_create_pad(len(block))  # create a pad
    # print(f'encryption pad for {msg}:\n{bytes(pad_bin, "ascii")}')

    enc_msg_to_send = encrypt(block, pad_bin.encode())
    # print(f'enc msg: {enc_msg_to_send}')

    # dec_msg = decrypt(enc_msg_to_send, bytes(pad_bin, 'ascii'))
    # print(f'************: {byte_to_text(dec_user_name)}')
    return enc_msg_to_send


def decrypt_cipher(cipher, pad):
    # print(f'enc res: {cipher}')
    pad_bin = pad.my_key_stream_create_pad(len(cipher))
    # print(f'decryption pad for {cipher}:\n{bytes(pad_bin, "ascii")}')

    cipher_dec = decrypt(cipher, bytes(pad_bin, 'ascii'))
    msg_from_server = byte_to_text(cipher_dec)
    # print(f'decrypt msg: {msg_from_server}')
    return msg_from_server

def decrypt_cipher_file(cipher, pad):
    # print(f'enc res: {cipher}')
    pad_bin = pad.my_key_stream_create_pad(len(cipher))
    # print(f'decryption pad for {cipher}:\n{bytes(pad_bin, "ascii")}')

    cipher_dec = decrypt(cipher, pad_bin.encode())
    # print(f'decrypt msg: {msg_from_server}')
    return cipher_dec


def start():
    global private_flag
    global data_list_for_private
    # step 1- client connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 1235))
    print(s.getsockname())
    # key exchange
    seed = key_exchange(s, random.choice(primes), random.choice(primes),
                        random.randint(10, 100))

    pad = SetSeed(seed)

    # step 2- client recieve questions from server
    enc_login_or_not = my_funcs.receive_data(s)
    login_or_not = decrypt_cipher(enc_login_or_not, pad)
    client_ans = input(login_or_not)
    s.send(encrypt_msg(client_ans, pad))

    success = False
    while not success and client_ans == '2':
        create_account = decrypt_cipher(my_funcs.receive_data(s), pad)
        print(create_account)

        first_name = input('first name: ')
        s.send(encrypt_msg(first_name, pad))
        if first_name == '0':
            break
        last_name = input('last name: ')
        s.send(encrypt_msg(last_name, pad))
        if last_name == '0':
            break
        user_name = input('user name: ')
        s.send(encrypt_msg(user_name, pad))
        if user_name == '0':
            break
        password = input('password: ')
        s.send(encrypt_msg(password, pad))
        if password == '0':
            break

        server_ans = decrypt_cipher(my_funcs.receive_data(s), pad)
        print(server_ans)
        if server_ans == 'details saved successfully':
            success = True

    success = False
    while not success:
        enc_enter_name = my_funcs.receive_data(s)
        print(decrypt_cipher(enc_enter_name, pad))
        username = input('user name: ')
        password = input('password: ')

        # step 3 - send to server the username
        s.send(encrypt_msg(username, pad))
        s.send(encrypt_msg(password, pad))

        try_to_login = decrypt_cipher(my_funcs.receive_data(s), pad)
        print(try_to_login)
        if try_to_login == 'success to connect':
            success = True
            print(decrypt_cipher(my_funcs.receive_data(s), pad))  # hello

    # step 4 - recive from server the online client in the chat
    enc_online_clients = my_funcs.receive_data(s)
    online_clients = decrypt_cipher(enc_online_clients, pad)
    print(online_clients)
    print('press 1 to exit')

    # step 5 - start reviving msg from server in different thread!!
    t1 = threading.Thread(target=recive_ongoing_msg_from_chat_server, args=(s, pad,))
    t1.start()

    print("You are connected to the server")
    # in LOOP forever!!!
    while True:
        # step 6- client send some msg to server (get the msg as input from the user)
        user_msg = input()
        if private_flag:
            if user_msg == '1':
                print('exit from private session')
                private_flag = False
                s.send(user_msg.encode())
                data_list_for_private.clear()
            else:
                enc_private_msg_to_send = encrypt_msg(user_msg, data_list_for_private[-1])
                s.send(enc_private_msg_to_send)
        else:
            if user_msg == '1' or user_msg == '***delete_account***':
                enc_msg_to_send = encrypt_msg(user_msg, pad)
                s.send(enc_msg_to_send)
                break

            enc_msg_to_send = encrypt_msg(user_msg, pad)

            s.send(enc_msg_to_send)

    print('client program exit!!')

def my_webcam():
    vid = cv2.VideoCapture(0)

    while vid.isOpened():
        img, frame = vid.read()
        frame = imutils.resize(frame, width=320)
        a = pickle.dumps(frame)
        message = struct.pack("Q", len(a)) + a

        enc_msg = encrypt_file(message, user_pad)
        s.send(enc_msg)

        cv2.imshow('MY VIDEO', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

def other_webcam(from_who):
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = my_funcs.receive_data(s)
            msg = decrypt_cipher_file(packet, user_pad)
            if not packet:
                break
            data += msg
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += my_funcs.receive_data(s)
            msg = decrypt_cipher_file(data, user_pad)
        frame_data = msg[:msg_size]
        msg = msg[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow(f'{from_who} VIDEO', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

def recive_ongoing_msg_from_chat_server_func_gui(s, pad, text_box):
    global private_flag
    while True:
        if not private_flag:
            enc_msg_from_server = my_funcs.receive_data(s)
            msg_from_server = decrypt_cipher(enc_msg_from_server, pad)  # msg from the server

            if msg_from_server == 'kill yourself':   # exit
                s.close()
                break


            if msg_from_server == 'get file photo':    # download a file
                enc_file_name_from_server = my_funcs.receive_data(s)
                file_name_from_server = decrypt_cipher(enc_file_name_from_server, pad)
                f = open(f'{user_name}_from_{file_name_from_server}', "wb")
                enc_block_file = my_funcs.receive_data(s)
                block_file = decrypt_cipher_file(enc_block_file, pad)
                digest_maker = hmac.new(str(seed_server).encode(), ''.encode(), hashlib.sha256)
                while block_file != b'0':
                    f.write(block_file)
                    # print(block_file)
                    # print(block_file.encode())
                    digest_maker.update(block_file)

                    enc_block_file = my_funcs.receive_data(s)
                    block_file = decrypt_cipher_file(enc_block_file, pad)
                    # print(block_file)
                    # print(block_file.encode())
                f.close()

                rec_digest = digest_maker.hexdigest()
                print(f'hmac for the content in the file that sent {rec_digest}')
                enc_real_digest = my_funcs.receive_data(s)
                real_digest = decrypt_cipher(enc_real_digest, pad)
                print(f'hmac for the real file {real_digest}')

                if real_digest == rec_digest:
                    text_box.configure(state=NORMAL)
                    text_box.insert(END, f'{file_name_from_server} file successfully downloaded')
                    text_box.insert(END, '\n')
                    text_box.configure(state=DISABLED)
                    text_box.see(END)
                    continue
                else:
                    text_box.configure(state=NORMAL)
                    text_box.insert(END, f'{file_name_from_server} file is distorted')
                    text_box.insert(END, '\n')
                    text_box.configure(state=DISABLED)
                    text_box.see(END)
                    continue


            if msg_from_server == 'start camera':
                enc_from_who = my_funcs.receive_data(s)
                from_who = decrypt_cipher(enc_from_who, pad)

                data = b""
                payload_size = struct.calcsize("Q")
                while True:
                    while len(data) < payload_size:
                        packet = my_funcs.receive_data(s)
                        #msg = decrypt_cipher_file(packet, user_pad)
                        if not packet:
                            break
                        data += packet
                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("Q", packed_msg_size)[0]

                    while len(data) < msg_size:
                        data += my_funcs.receive_data(s)
                        #msg = decrypt_cipher_file(data, user_pad)
                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    frame = pickle.loads(frame_data)
                    cv2.imshow(f'{from_who} VIDEO', frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == 20:
                        break
                cv2.destroyAllWindows()


            if msg_from_server == 'creator_rsa':    # the client that wants to start private session, create the keys
                key_exchange_for_private(s, random.choice(primes), random.choice(primes),
                                         random.randint(10, 100))
                private_flag = True

            if msg_from_server == 'second_participant':    # the second client in the private session create the key, encrypt it and send back
                public_key = int(my_funcs.receive_data_with_decode(s))
                print(public_key)
                qp = int(my_funcs.receive_data_with_decode(s))
                print(qp)
                data_list_for_private.append(qp)
                data_list_for_private.append(public_key)
                seed = random.randint(0, 500)
                print(f'seed_for_private2    {seed}')
                data_list_for_private.append(SetSeed(seed, 8888, 9999))
                enc_seed = my_funcs.rsa_encryption_decryption(qp, public_key, seed)
                print(f'enc seed_for_private2    {enc_seed}')
                s.send(str(enc_seed).encode())
                private_flag = True

            print(msg_from_server)

            text_box.configure(state=NORMAL)
            text_box.insert(END, msg_from_server)
            text_box.insert(END, '\n')
            text_box.configure(state=DISABLED)
            text_box.see(END)
        else:                                                       # the client in a private session
            enc_private_msg_from_server = my_funcs.receive_data(s)
            if enc_private_msg_from_server == '1'.encode():        # exit from the private session
                s.send('stam'.encode())
                private_flag = False
                data_list_for_private.clear()

                print('exit from private session')
                text_box.configure(state=NORMAL)
                text_box.insert(END, 'exit from private session')
                text_box.insert(END, '\n')
                text_box.configure(state=DISABLED)
                text_box.see(END)
            else:
                if private_flag:
                    private_msg_from_server = decrypt_cipher(enc_private_msg_from_server, data_list_for_private[-1])

                    print(private_msg_from_server)

                    text_box.configure(state=NORMAL)
                    text_box.insert(END, private_msg_from_server)
                    text_box.insert(END, '\n')
                    text_box.configure(state=DISABLED)
                    text_box.see(END)
    exit()


def start_func(login_or_create):
    global private_flag
    global data_list_for_private
    global user_pad
    global s
    global seed_server

    # step 1- client connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 23850))                        #**************************************
    print(s.getsockname())
    # key exchange
    seed_a_b = key_exchange(s, random.choice(primes), random.choice(primes),
                        random.randint(10, 100))
    seed_server = seed_a_b[0]

    #globals()['user_pad'] = SetSeed(seed_a_b[0], seed_a_b[1], seed_a_b[2])  # obj that will help to generate pads for the server
    user_pad = SetSeed(seed_a_b[0], seed_a_b[1], seed_a_b[2])  # obj that will help to generate pads for the server

    print("MY USER PAD : ")
    print(user_pad.start_seed)
    print(user_pad.A)
    print(user_pad.B)

    enc_login_or_not = my_funcs.receive_data(s)
    login_or_not = decrypt_cipher(enc_login_or_not, user_pad)
    print(login_or_not)
    client_ans = login_or_create      # what the user click on
    s.send(encrypt_msg(client_ans, user_pad))

    create_account = decrypt_cipher(my_funcs.receive_data(s), user_pad)
    print(create_account)


def login_func(username, password):
    global user_name
    # step 3 - send to server the username
    s.send(encrypt_msg(username, user_pad))
    s.send(encrypt_msg(password, user_pad))

    try_to_login = decrypt_cipher(my_funcs.receive_data(s), user_pad)
    print(try_to_login)

    print("MY USER PAD : ")
    print(user_pad.start_seed)
    print(user_pad.A)
    print(user_pad.B)

    if try_to_login == 'success to connect':
        user_name = username
        print(decrypt_cipher(my_funcs.receive_data(s), user_pad))  # hello
        return True
    else:
        return False


def create_account_func(params_list):
    if '0' in params_list:
        return '0'

    for param in params_list:
        s.send(encrypt_msg(param, user_pad))
        time.sleep(0.01)

    server_ans = decrypt_cipher(my_funcs.receive_data(s), user_pad)
    print(server_ans)
    if server_ans == 'details saved successfully':
        return '1'
    else:
        return '2'


def select_room_func(room):
    print("MY USER PAD : ")
    print(user_pad.start_seed)
    print(user_pad.A)
    print(user_pad.B)
    enc_which_room = my_funcs.receive_data(s)
    #print(enc_which_room)
    which_room = decrypt_cipher(enc_which_room, user_pad)
    print(which_room)
    print('press 1 to exit')

    print("You are connected to the server")

    enc_msg_to_send = encrypt_msg(room, user_pad)
    s.send(enc_msg_to_send)

    return user_name


def start_receive(textbox):
    # step 5 - start reviving msg from server in different thread!!
    t1 = threading.Thread(target=recive_ongoing_msg_from_chat_server_func_gui, args=(s, user_pad, textbox))
    t1.start()


def session_func(user_msg, textbox):
    global private_flag
    global data_list_for_private
    global hmac_flag_txt
    global hmac_flag_photo
    global hack_flag

    # step 6- client send some msg to server (get the msg as input from the user)
    if private_flag:     # the client in a private session
        if user_msg == '1':
            print('exit from private session')
            textbox.configure(state=NORMAL)
            textbox.insert(END, 'exit from private session')
            textbox.insert(END, '\n')
            textbox.configure(state=DISABLED)
            textbox.see(END)
            private_flag = False
            s.send(user_msg.encode())
            data_list_for_private.clear()
            return 'continue'
        else:
            enc_private_msg_to_send = encrypt_msg(user_msg, data_list_for_private[-1])
            s.send(enc_private_msg_to_send)
            return 'continue'
    else:
        if user_msg == '1' or user_msg == '***delete_account***':   # exit
            enc_msg_to_send = encrypt_msg(user_msg, user_pad)
            s.send(enc_msg_to_send)
            return 'exit'

        #  FILES
        if hmac_flag_photo:   # send file
            try:
                f = open(user_msg)
                f.close()
            except IOError:
                print("File not accessible")
                enc_file_name_to_send = encrypt_msg('File not accessible', user_pad)
                s.send(enc_file_name_to_send)
                hmac_flag_photo = False
                return 'File not accessible'

            enc_file_name_to_send = encrypt_msg(user_msg, user_pad)
            s.send(enc_file_name_to_send)

            file_name_hmac = hmac.new(str(seed_server).encode(), user_msg.encode(), hashlib.sha256).hexdigest()
            enc_file_name_hmac_to_send = encrypt_msg(file_name_hmac, user_pad)
            s.send(enc_file_name_hmac_to_send)

            digest_maker = hmac.new(str(seed_server).encode(), ''.encode(), hashlib.sha256)
            try:
                f = open(user_msg, 'rb')
                try:
                    block = f.read(1024)
                    while block:
                        # print('*')
                        digest_maker.update(block)
                        print('*')
                        print(block)
                        enc_block_to_send = encrypt_file(block, user_pad)
                        print('**')
                        print(enc_block_to_send)
                        if hack_flag:     # פורץ משבש את תוכן הקובץ
                            s.send(len(enc_block_to_send) * b'0')
                        else:
                            s.send(enc_block_to_send)
                        # print(block)
                        # print(block.decode())  # block
                        # print('***')

                        block = f.read(1024)
                finally:
                    f.close()
                    hack_flag = False
                time.sleep(0.2)
                enc_block_to_send = encrypt_file(b'0', user_pad)
                s.send(enc_block_to_send)

                time.sleep(0.05)

                digest = digest_maker.hexdigest()
                print(f'hmac for the real file {digest}')

                enc_digest_to_send = encrypt_msg(digest, user_pad)
                s.send(enc_digest_to_send)

            except:
                pass
            hmac_flag_photo = False
            return 'sent'


        if user_msg == 'FILE':
            hmac_flag_photo = True

        if user_msg == 'HACK':     # disrupt the information
            hack_flag = True
            return

        #  webcam share
        if user_msg == 'WEBCAM':
            c = 0
            enc_msg_to_send = encrypt_msg(user_msg, user_pad)
            s.send(enc_msg_to_send)
            time.sleep(0.01)
            vid = cv2.VideoCapture(0)
            while vid.isOpened():
                c += 1
                img, frame = vid.read()
                frame = imutils.resize(frame, width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                # enc_msg = encrypt_file(message, user_pad)
                s.send(message)
                cv2.imshow('MY VIDEO', frame)
                key = cv2.waitKey(1) & 0xFF
                print(c)
                if c < 600:
                    cv2.destroyAllWindows()
                    break
            return
        enc_msg_to_send = encrypt_msg(user_msg, user_pad)
        # print(enc_msg_to_send)
        # print(type(enc_msg_to_send))
        s.send(enc_msg_to_send)
        return 'continue'

#start()

