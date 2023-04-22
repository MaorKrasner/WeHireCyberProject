import os
import socket
import threading
import time
from chat_database_management import *
from ChatDirectory import my_funcs
from otp_funcs import *
from cryptography.fernet import Fernet
import logging
import hashlib
import hmac

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{',
    filename='serverLog.log',
    filemode='w'
)

client_seeds = {}  # the server save the public key, the pq, the seed and the SetSeed obj for each client socket
clients = {}
clients_room_work = {}
clients_room_talking = {}
clients_room_dating = {}
clients_users = {}  # for each user name the server save his first name, last name and his password
client_password_key = {}  # for each user name the server save his password_key for his password
insert_data_from_db_to_clients_users(clients_users)
print(clients_users)
private_sessions = {}


def key_exchange(client_socket):
    ab = []
    public_key_and_pq = my_funcs.receive_data_with_decode(client_socket)  # get the public key and the pq
    client_seeds[client_socket] = [int(i) for i in public_key_and_pq.split(' ')]  # first public key second pq
    # print(f'public key    {client_seeds[client_socket][0]}')
    # print(f'pq    {client_seeds[client_socket][1]}')
    logging.info(f'public key    {client_seeds[client_socket][0]}')
    logging.info(f'pq    {client_seeds[client_socket][1]}')

    # create the seed randomali and send it to the client
    seed = random.randint(0, 5000)
    a = random.randint(10, 99)
    ab.append(a)
    print(f'a    {ab[0]}')
    b = random.randint(10, 99)
    ab.append(b)
    print(f'b    {ab[1]}')

    client_seeds[client_socket].append(seed)  # third seed
    # print(f'real seed    {seed}')
    logging.info(f'real seed    {seed}')
    # encrypt the seed
    enc_seed = my_funcs.rsa_encryption_decryption(client_seeds[client_socket][1], client_seeds[client_socket][0],
                                                  client_seeds[client_socket][2])
    # print(f'enc seed    {enc_seed}')
    logging.info(f'enc seed    {enc_seed}')
    # print(f'enc_seed    {type(enc_seed)}')
    logging.info('_________________next_client_________________')
    # send it to the client
    client_socket.send(str(enc_seed).encode())  # send the enc seed to the client

    enc_a = my_funcs.rsa_encryption_decryption(client_seeds[client_socket][1], client_seeds[client_socket][0], ab[0])
    print(f'enc_a    {enc_a}')
    # print(f'enc_a    {type(enc_a)}')
    client_socket.send(str(enc_a).encode())

    time.sleep(1)

    enc_b = my_funcs.rsa_encryption_decryption(client_seeds[client_socket][1], client_seeds[client_socket][0], ab[1])
    print(f'enc_b    {enc_b}')
    client_socket.send(str(enc_b).encode())

    ab[0] = int(str(a) + str(b))
    ab[1] = int(str(b) + str(a))
    return ab


def encrypt_msg(msg, pad):
    msg_bin = text_to_byte(msg)
    pad_bin = pad.my_key_stream_create_pad(len(msg_bin))  # create a pad
    # print(f'encryption pad for {msg}:\n{bytes(pad_bin, "ascii")}')

    enc_msg_to_send = encrypt(bytes(msg_bin, 'ascii'), bytes(pad_bin, 'ascii'))
    # print(f'enc msg: {enc_msg_to_send}')

    # dec_msg = decrypt(enc_msg_to_send, bytes(pad_bin, 'ascii'))
    # print(f'************: {byte_to_text(dec_user_name)}')
    return enc_msg_to_send


def encrypt_msg_file(block, pad):
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
    msg_from_client = byte_to_text(cipher_dec)
    # print(f'decrypt msg: {msg_from_client}')
    return msg_from_client


def decrypt_cipher_file(cipher, pad):
    # print(f'enc res: {cipher}')
    pad_bin = pad.my_key_stream_create_pad(len(cipher))
    # print(f'decryption pad for {cipher}:\n{bytes(pad_bin, "ascii")}')

    cipher_dec = decrypt(cipher, pad_bin.encode())
    # print(f'decrypt msg: {msg_from_client}')
    return cipher_dec


def sending_frames_thread(room, client_s):
    enc_frame = my_funcs.receive_data(client_s)
    while enc_frame:
        for others_clients in room.values():
            if others_clients is not client_s:
                if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [
                    clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                    others_clients.send(encrypt_msg_file(enc_frame, client_seeds[others_clients][3]))

        enc_frame = my_funcs.receive_data(client_s)


def session_with_client(client_socket):  # start the session
    ab = key_exchange(client_socket)

    current_room = {}

    pad = SetSeed(client_seeds[client_socket][2], ab[0], ab[1])  # <--seed
    client_seeds[client_socket].append(pad)
    # print(len(str(client_socket)))
    # print(len(str(client_seeds[client_socket][3])))

    insert_row_into_table("client_seeds", (
    str(client_socket), client_seeds[client_socket][0], client_seeds[client_socket][1], client_seeds[client_socket][2],
    str(client_seeds[client_socket][3])))
    # insert_rec_to_client_seeds_table(str(client_socket), client_seeds[client_socket][0], client_seeds[client_socket][1], client_seeds[client_socket][2], str(client_seeds[client_socket][3]))  # add to db

    # client_seeds[client_socket][3] = pad ---> each client_socket

    # key for encrypt the password in the database

    # step 1 - server send msg 1 to client
    msg_to_send = "to login send 1, to create account send 2"
    enc_msg_to_send = encrypt_msg(msg_to_send, client_seeds[client_socket][3])

    client_socket.send(enc_msg_to_send)

    enc_ans = my_funcs.receive_data(client_socket)
    if enc_ans == -999:
        return

    ans = decrypt_cipher(enc_ans, client_seeds[client_socket][3])

    if ans == '2':
        msg_to_send = "choose your first name, last name, user name and the password you want(with a enter between each) to login send 0"
        client_socket.send(encrypt_msg(msg_to_send, client_seeds[client_socket][3]))
    elif ans == '1':
        msg_to_send = "what is your user name and your password?"
        client_socket.send(encrypt_msg(msg_to_send, client_seeds[client_socket][3]))

    success = False
    while not success and ans == '2':  # create account
        first_name = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])
        last_name = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])
        user_name = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])
        password = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])
        user_type = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])
        user_ID = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])
        company_name = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])

        if '0' in [first_name, last_name, user_name, password, user_type, user_ID, company_name]:
            break

        if user_name in clients_users.keys():
            client_socket.send(
                encrypt_msg("the user name already used, please try again", client_seeds[client_socket][3]))
        else:
            client_socket.send(encrypt_msg("details saved successfully", client_seeds[client_socket][3]))

            # encrypt the password to the database
            key = Fernet.generate_key()

            insert_row_into_table("client_password_key", (user_name, key.decode()))
            # insert_rec_to_client_password_key_table(user_name, key.decode())

            f_obj = Fernet(key)

            # print(f'key: {key} for user: {user_name}')
            msg = password.encode()
            encrypted_msg = f_obj.encrypt(msg)
            # print(encrpted_msg.decode())
            # to decrypt
            '''# decrypting string message with the key
            decrypted_msg = f_obj.decrypt(encrpted_msg)
            print(decrypted_msg.decode)'''

            insert_row_into_table("client_user",
                                  (user_name, first_name, last_name, encrypted_msg.decode(), user_type, user_ID, company_name))

            # insert_rec_to_client_user_table(user_name, first_name, last_name, encrpted_msg.decode())

            client_password_key[user_name] = f_obj
            clients_users[user_name] = [first_name, last_name, password]
            success = True

    success = False
    while not success:  # login
        print("IM HERE!!!")
        user_name = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])
        print(user_name)
        password = decrypt_cipher(my_funcs.receive_data(client_socket), client_seeds[client_socket][3])
        print(password)

        print("1234")

        if user_name in clients_users and (Fernet(show_key_of_specific_rec_client_password_key_table(user_name).encode()).decrypt(show_password_of_specific_rec_client_user_table(user_name).encode())).decode() == password and user_name not in clients:
            success = True
            print(str(success) + "!!!!!!!!")
            client_socket.send(encrypt_msg("success to connect", client_seeds[client_socket][3]))
            client_socket.send(encrypt_msg(f'hello {user_name}:', client_seeds[client_socket][3]))
        else:
            client_socket.send(encrypt_msg('failed to connect', client_seeds[client_socket][3]))
            print("False!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    insert_row_into_table("client_user_socket", (user_name, str(client_socket)))
    # insert_rec_to_client_socket_table(user_name, str(client_socket))

    # step 2 - server wait to recieve the username from the client
    # add the current client to dict
    clients[user_name] = client_socket
    print(f'client {user_name} data: {client_seeds[client_socket]}')  # the public key, pq, seed and SetSeed obj

    # step 3 - server send list of online clinets
    '''online_clients = ' '.join(clients.keys())
    msg_to_send = "current online clients:" + online_clients
    enc_msg_to_send = encrypt_msg(msg_to_send, client_seeds[client_socket][3])
    client_socket.send(enc_msg_to_send)'''

    # print(clients.values())

    flag_session = True
    time.sleep(0.1)

    '''
    # enter room
    client_socket.send(encrypt_msg("Which room would you like to join - work, talking, dating", client_seeds[client_socket][3]))
    '''

    enc_room = my_funcs.receive_data(client_socket)

    room = decrypt_cipher(enc_room, client_seeds[client_socket][3])

    if room == 'work':
        clients_room_work[user_name] = client_socket
        current_room = clients_room_work
    elif room == 'dating':
        clients_room_dating[user_name] = client_socket
        current_room = clients_room_dating
    else:
        clients_room_talking[user_name] = client_socket
        current_room = clients_room_talking
        room = 'talking'

    '''enc_msg_to_send = encrypt_msg(f'You are connecting to {room} room.', client_seeds[client_socket][3])
    client_socket.send(enc_msg_to_send)'''

    # in LOOP!!!
    while flag_session:

        # 4 - recieve client_msg from client
        msg_header = f'{user_name}: '
        msg_header_private = f'{user_name} (private): '

        if [user_name, 3] in private_sessions.values():  # part 5                                                # creator
            for tuple_private in private_sessions.items():  # tuple_private = (sec_user, me)
                if tuple_private[1][0] == user_name:
                    sec_user = tuple_private[0]
                    break
            print('c')
            enc_private_msg_from_client = my_funcs.receive_data(client_socket)
            if enc_private_msg_from_client == '1'.encode():
                private_sessions.pop(sec_user)
            clients[sec_user].send(enc_private_msg_from_client)

        if user_name in private_sessions.keys() and private_sessions[user_name][1] == 3:  # part 5                # second
            sec_userr = private_sessions[user_name][0]
            if user_name not in private_sessions.keys():
                continue
            print('s')
            enc_private_msg_from_client = my_funcs.receive_data(client_socket)
            if enc_private_msg_from_client == '1'.encode():
                private_sessions.pop(user_name)
            clients[sec_userr].send(enc_private_msg_from_client)
        else:
            if [user_name, 1] in private_sessions.values():  # part 3
                for (sec_user, me) in private_sessions.items():
                    if me[0] == user_name:
                        break
                print('***')
                public_key_private = my_funcs.receive_data(client_socket)
                print(f'public key from c {public_key_private};')
                pq_private = my_funcs.receive_data(client_socket)
                print(f'pq key from c {pq_private};')
                clients[sec_user].send(encrypt_msg('second_participant', client_seeds[clients[sec_user]][3]))
                clients[sec_user].send(public_key_private)
                time.sleep(0.05)
                clients[sec_user].send(pq_private)
                private_sessions[sec_user][1] = 2

            if user_name in private_sessions.keys() and private_sessions[user_name][1] == 2:  # part 4
                print('****')
                enc_seed = my_funcs.receive_data(client_socket)
                clients[private_sessions[user_name][0]].send(enc_seed)
                private_sessions[user_name][1] = 3

            if [user_name, 0] in private_sessions.values() or [user_name, 1] in private_sessions.values() or [user_name,
                                                                                                              2] in private_sessions.values() or [
                user_name, 3] in private_sessions.values():
                pass
            elif user_name in private_sessions.keys() and (
                    private_sessions.get(user_name)[1] == 1 or private_sessions.get(user_name)[1] == 2 or
                    private_sessions.get(user_name)[1] == 3):
                pass
            else:

                enc_msg_from_client = my_funcs.receive_data(client_socket)
                # print(f'data enc {enc_msg_from_client}')
                # print(type(enc_msg_from_client))
                msg_from_client = decrypt_cipher(enc_msg_from_client, client_seeds[client_socket][3])
                # print(f'data dec {msg_from_client}')

                '''
                for word in msg_from_client.split(' '):
                    if word.upper() in detectEnglish.loadDictionary_list():   # documentation suspicious messages
                        insert_sus_msg_to_specific_room(user_name, msg_from_client, room)
                '''

                if user_name in private_sessions.keys():  # part 2
                    if private_sessions[user_name][1] == 0:  # need to answer to private session
                        print('**')
                        if msg_from_client == 'decline_p':
                            clients[private_sessions[user_name][0]].send(
                                encrypt_msg(f'{user_name} declined to start a private session with you',
                                            client_seeds[clients[private_sessions[user_name][0]]][3]))
                            private_sessions.pop(user_name)
                        elif msg_from_client == 'confirm_p':
                            clients[private_sessions[user_name][0]].send(
                                encrypt_msg(f'{user_name} confirmed to start a private session with you',
                                            client_seeds[clients[private_sessions[user_name][0]]][3]))
                            private_sessions[user_name][1] = 1
                            clients[private_sessions[user_name][0]].send(
                                encrypt_msg('creator_rsa', client_seeds[clients[private_sessions[user_name][0]]][3]))

                else:

                    if msg_from_client == '1':
                        client_socket.send(encrypt_msg('kill yourself', client_seeds[client_socket][3]))
                        clients.pop(user_name)
                        current_room.pop(user_name)
                        client_seeds.pop(client_socket)

                        delete_rec_from_client_seeds_table(str(client_socket))  # delete from db
                        delete_rec_from_client_socket_table(str(client_socket))

                        for others_clients in current_room.values():
                            if others_clients is not client_socket:
                                if others_clients not in [clients[c] for c in
                                                          private_sessions.keys()] and others_clients not in [
                                    clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                    enc_left_msg_to_others = encrypt_msg(f'{user_name} is left the session',
                                                                         client_seeds[others_clients][3])
                                    others_clients.send(enc_left_msg_to_others)
                        break

                    if msg_from_client == '***delete_account***':  # delete the account and exit
                        # client_socket.send(encrypt_msg('Your account has been deleted', client_seeds[client_socket][3]))
                        client_socket.send(encrypt_msg('kill yourself', client_seeds[client_socket][3]))

                        delete_rec_from_client_user_table(user_name)  # delete from db
                        delete_rec_from_client_seeds_table(str(client_socket))
                        delete_rec_from_client_socket_table(str(client_socket))
                        delete_rec_from_client_password_key_table(user_name)

                        clients.pop(user_name)
                        current_room.pop(user_name)
                        client_seeds.pop(client_socket)
                        clients_users.pop(user_name)

                        for others_clients in current_room.values():
                            if others_clients is not client_socket:
                                if others_clients not in [clients[c] for c in
                                                          private_sessions.keys()] and others_clients not in [
                                    clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                    enc_left_msg_to_others = encrypt_msg(f'{user_name} is left the session',
                                                                         client_seeds[others_clients][3])
                                    others_clients.send(enc_left_msg_to_others)
                        break

                    if msg_from_client == '!online':  # show the connected clients
                        online_clients = ' '.join(clients.keys())
                        client_socket.send(
                            encrypt_msg(('current online clients:' + online_clients), client_seeds[client_socket][3]))

                    elif msg_from_client == 'FILE':  # file
                        enc_file_name = my_funcs.receive_data(client_socket)
                        file_name = decrypt_cipher(enc_file_name, client_seeds[client_socket][3])

                        if file_name == 'File not accessible':  # if there is no file called that
                            continue

                        enc_file_name_hmac = my_funcs.receive_data(client_socket)
                        file_name_hmac = decrypt_cipher(enc_file_name_hmac, client_seeds[client_socket][3])

                        if hmac.new(str(client_seeds[client_socket][2]).encode(), file_name.encode(),
                                    hashlib.sha256).hexdigest() == file_name_hmac:  # check the integrity of the file name
                            f = open(f"server_temp_file.{file_name.split('.')[-1]}", "wb")

                            real_digest_maker = hmac.new(str(client_seeds[client_socket][2]).encode(), ''.encode(),
                                                         hashlib.sha256)

                            enc_block_file = my_funcs.receive_data(client_socket)
                            # print(enc_block_file)
                            block_file = decrypt_cipher_file(enc_block_file, client_seeds[client_socket][3])
                            # print(block_file)
                            # print(type(block_file))

                            while block_file != b'0':  # get the file
                                print('*')
                                f.write(block_file)
                                # print('*')
                                real_digest_maker.update(block_file)

                                enc_block_file = my_funcs.receive_data(client_socket)
                                block_file = decrypt_cipher_file(enc_block_file, client_seeds[client_socket][3])
                                print(block_file)
                                # print(block_file)
                                # print(block_file.encode())

                            f.close()

                            real_digest = real_digest_maker.hexdigest()
                            print(f'hmac for the content in the file that sent {real_digest}')

                            enc_body_file_hmac = my_funcs.receive_data(client_socket)
                            body_file_hmac = decrypt_cipher(enc_body_file_hmac, client_seeds[client_socket][3])
                            print(f'hmac for the real file {body_file_hmac}')

                            if real_digest == body_file_hmac:  # check the integrity of the file body
                                print(f'The FILE sent from {user_name} are original')
                                for others_clients in current_room.values():
                                    if others_clients is not client_socket:
                                        if others_clients not in [clients[c] for c in
                                                                  private_sessions.keys()] and others_clients not in [
                                            clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                            others_clients.send(
                                                encrypt_msg('get file photo', client_seeds[others_clients][3]))
                                            time.sleep(0.5)
                                            others_clients.send(
                                                encrypt_msg(f'{user_name}_{os.path.basename(file_name)}',
                                                            client_seeds[others_clients][3]))
                                time.sleep(0.1)

                                hmac_for_clients = {}
                                for others_clients in current_room.values():
                                    if others_clients is not client_socket:
                                        hmac_for_clients[others_clients] = hmac.new(
                                            str(client_seeds[others_clients][2]).encode(), ''.encode(), hashlib.sha256)

                                f = open(f"server_temp_file.{file_name.split('.')[-1]}", "rb")
                                block = f.read(1024)

                                while block:  # sending the file to all clients
                                    # print('**')
                                    # print(block)
                                    # print(block.decode())
                                    for others_clients in current_room.values():
                                        if others_clients is not client_socket:
                                            if others_clients not in [clients[c] for c in
                                                                      private_sessions.keys()] and others_clients not in [
                                                clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                                hmac_for_clients[others_clients].update(block)
                                                others_clients.send(
                                                    encrypt_msg_file(block, client_seeds[others_clients][3]))
                                    time.sleep(0.1)

                                    block = f.read(1024)
                                f.close()

                                # os.remove("server_temp_file.txt")
                                time.sleep(0.5)
                                for others_clients in current_room.values():
                                    if others_clients is not client_socket:
                                        if others_clients not in [clients[c] for c in
                                                                  private_sessions.keys()] and others_clients not in [
                                            clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                            others_clients.send(encrypt_msg_file(b'0', client_seeds[others_clients][3]))

                                time.sleep(0.1)
                                for others_clients in current_room.values():
                                    if others_clients is not client_socket:
                                        if others_clients not in [clients[c] for c in
                                                                  private_sessions.keys()] and others_clients not in [
                                            clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                            others_clients.send(
                                                encrypt_msg(hmac_for_clients[others_clients].hexdigest(),
                                                            client_seeds[others_clients][3]))

                                hmac_for_clients.clear()

                            else:
                                print(f'Something change in the FILE sent from {user_name} 2')
                        else:
                            print(f'Something change in the FILE sent from {user_name} 1')

                    elif msg_from_client == '!room online':  # show the connected clients
                        online_clients = ' '.join(current_room.keys())
                        client_socket.send(encrypt_msg((f'current online clients in {room} room:' + online_clients),
                                                       client_seeds[client_socket][3]))

                    elif msg_from_client == '!profile':  # show the first name and the last name for specific online client
                        enc_to_who = my_funcs.receive_data(client_socket)
                        to_who = decrypt_cipher(enc_to_who, client_seeds[client_socket][3])
                        online_clients = (' '.join(clients.keys())).split(' ')
                        if to_who in online_clients:
                            client_socket.send(encrypt_msg(
                                f'{to_who}:\nfirst name: {clients_users[to_who][0]}.\nlast name: {clients_users[to_who][1]}.',
                                client_seeds[client_socket][3]))
                        else:
                            client_socket.send(
                                encrypt_msg(f'{to_who} are not online right now', client_seeds[client_socket][3]))

                    elif msg_from_client == 'WEBCAM':  # camera share

                        for others_clients in current_room.values():
                            if others_clients is not client_socket:
                                if others_clients not in [clients[c] for c in
                                                          private_sessions.keys()] and others_clients not in [
                                    clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                    others_clients.send(encrypt_msg('start camera', client_seeds[others_clients][3]))
                                    others_clients.send(encrypt_msg(user_name, client_seeds[others_clients][3]))

                        enc_frame = my_funcs.receive_data(client_socket)
                        # print('*')
                        while enc_frame:
                            # print('**')
                            for others_clients in current_room.values():
                                if others_clients is not client_socket:
                                    if others_clients not in [clients[c] for c in
                                                              private_sessions.keys()] and others_clients not in [
                                        clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                        others_clients.send(enc_frame)

                            enc_frame = my_funcs.receive_data(client_socket)

                    elif msg_from_client == '!private':  # trying to start private msg   # part 1
                        print('*')
                        enc_to_who = my_funcs.receive_data(client_socket)
                        to_who = decrypt_cipher(enc_to_who, client_seeds[client_socket][3])
                        if to_who in clients.keys() and to_who != user_name:
                            # enc_private_msg = my_funcs.receive_data(client_socket)
                            # private_msg = decrypt_cipher(enc_private_msg, client_seeds[client_socket][3])
                            # private_msg = msg_header_private + private_msg
                            if to_who in private_sessions.keys():
                                client_socket.send(encrypt_msg(f'ERROR: {to_who} already in private session',
                                                               client_seeds[client_socket][3]))
                            else:
                                private_sessions[to_who] = [user_name, 0]
                                accept_to_private_session_msg = f'{user_name} wants to start a private session with you. (confirm_p/decline_p)'
                                clients[to_who].send(
                                    encrypt_msg(accept_to_private_session_msg, client_seeds[clients[to_who]][3]))
                        else:
                            if to_who == user_name:
                                client_socket.send(
                                    encrypt_msg(f'ERROR: you can not start a private session with yourself',
                                                client_seeds[client_socket][3]))
                            else:
                                client_socket.send(encrypt_msg(f'ERROR: there is no client called {to_who}',
                                                               client_seeds[client_socket][3]))
                    else:
                        msg_from_client_to_others = msg_header + msg_from_client
                        for others_clients in current_room.values():
                            if others_clients is not client_socket:
                                if others_clients not in [clients[c] for c in
                                                          private_sessions.keys()] and others_clients not in [
                                    clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                    others_clients.send(
                                        encrypt_msg(msg_from_client_to_others, client_seeds[others_clients][3]))


# create server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind ip and port to socket
s.bind(('0.0.0.0', 23850))
# s.bind(('192.168.127.57', 1235))                      #**************************************
# set client queue to 5
s.listen(10)

# server is listening all the time!!!
while True:
    print('server is listening..')
    client_socket, address = s.accept()
    print(f'connection from {address} has been established')
    logging.info(f'connection from {address} has been established')

    t1 = threading.Thread(target=session_with_client, args=(client_socket,))
    t1.start()
