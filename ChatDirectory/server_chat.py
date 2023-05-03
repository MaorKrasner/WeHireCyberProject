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
clients_room_1 = {}
clients_room_2 = {}
clients_room_3 = {}
clients_list_of_rooms = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]  # a list of available rooms
clients_users = {}  # for each username the server save his first name, last name and his password
client_password_key = {}  # for each username the server save his password_key for his password
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
    logging.info(f'real seed    {seed}')
    # encrypt the seed
    enc_seed = my_funcs.rsa_encryption_decryption(client_seeds[client_socket][1], client_seeds[client_socket][0],
                                                  client_seeds[client_socket][2])
    logging.info(f'enc seed    {enc_seed}')
    logging.info('_________________next_client_________________')
    # send it to the client
    client_socket.send(str(enc_seed).encode())  # send the enc seed to the client

    enc_a = my_funcs.rsa_encryption_decryption(client_seeds[client_socket][1], client_seeds[client_socket][0], ab[0])
    print(f'enc_a    {enc_a}')
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
    #global user_name
    #user_name = ''
    ab = key_exchange(client_socket)

    current_room = {}

    pad = SetSeed(client_seeds[client_socket][2], ab[0], ab[1])  # <--seed
    client_seeds[client_socket].append(pad)

    # add to db
    insert_row_into_table("client_seeds", (
    str(client_socket), client_seeds[client_socket][0], client_seeds[client_socket][1], client_seeds[client_socket][2],
    str(client_seeds[client_socket][3])))

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

            f_obj = Fernet(key)

            msg = password.encode()
            encrypted_msg = f_obj.encrypt(msg)

            insert_row_into_table("client_user",
                                  (user_name, first_name, last_name, encrypted_msg.decode(), user_type, user_ID, company_name))

            client_password_key[user_name] = f_obj
            clients_users[user_name] = [first_name, last_name, password, user_type, user_ID, company_name]
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

    # step 2 - server wait to recieve the username from the client
    # add the current client to dict

    clients[user_name] = client_socket

    flag_session = True
    time.sleep(0.5)

    print("SEED ------------------")
    print(client_seeds[client_socket][3].start_seed)
    print(client_seeds[client_socket][3].A)
    print(client_seeds[client_socket][3].B)

    '''
    room_flag = False
    room_number = 0

    while not room_flag:
        # try to enter a specific room
        client_socket.send(encrypt_msg("Which room would you like to join ?", client_seeds[client_socket][3]))
        enc_room = my_funcs.receive_data(client_socket)
        room = decrypt_cipher(enc_room, client_seeds[client_socket][3])
        room_number = int(room.split(" ")[1])

        if len(clients_list_of_rooms[room_number - 1]) < 2:
            current_room = clients_list_of_rooms[room_number - 1]
            clients_list_of_rooms[room_number - 1][user_name] = client_socket
            client_socket.send(encrypt_msg(f'You are connected to {room}.', client_seeds[client_socket][3]))
            room_flag = True

        else:
            client_socket.send(encrypt_msg(f'You have chosen a room full of clients, try again!', client_seeds[client_socket][3]))
    '''

    # in LOOP!!!
    while flag_session:
        # headers for messages from the client
        msg_header = f'{user_name}: '

        sec_user = None

        if [user_name, 'received seed'] in private_sessions.values():        # part 5 - current user is the rsa creator
            for tuple_private in private_sessions.items():     # tuple_private = (sec_user, [me, status])
                if tuple_private[1][0] == user_name:
                    sec_user = tuple_private[0]
                    private_sessions[user_name] = [sec_user, 'received seed']
                    break
            print('c')
            enc_private_msg_from_client = my_funcs.receive_data(client_socket)
            if enc_private_msg_from_client == '1'.encode():
                print("OPTION 1 : ")
                print("Private sessions keys : " + str(private_sessions.keys()))
                print("Private sessions values : " + str(private_sessions.values()))
                private_sessions.pop(sec_user)
                private_sessions.pop(user_name)
            clients[sec_user].send(enc_private_msg_from_client)

        if user_name in private_sessions.keys() and private_sessions[user_name][1] == 'received seed':
            second_user = private_sessions[user_name][0]
            private_sessions[second_user] = [user_name, 'received seed']
            print('s')
            enc_private_msg_from_client = my_funcs.receive_data(client_socket)
            if enc_private_msg_from_client == '1'.encode():
                private_sessions.pop(user_name)
                private_sessions.pop(second_user)
                print("OPTION 2 : ")
                print("Private sessions keys : " + str(private_sessions.keys()))
                print("Private sessions values : " + str(private_sessions.values()))
            clients[second_user].send(enc_private_msg_from_client)

        else:
            if [user_name, 'accepted request'] in private_sessions.values():    # part 5 - current user is the second user
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
                private_sessions[sec_user][1] = 'received public key and pq'

            if user_name in private_sessions.keys() and private_sessions[user_name][1] == 'received public key and pq':   # part 4
                print('****')
                enc_seed = my_funcs.receive_data(client_socket)
                clients[private_sessions[user_name][0]].send(enc_seed)
                private_sessions[user_name][1] = 'received seed'

            if [user_name, 'initialized'] in private_sessions.values() \
                    or [user_name, 'accepted request'] in private_sessions.values() \
                    or [user_name, 'received public key and pq'] in private_sessions.values() \
                    or [user_name, 'received seed'] in private_sessions.values():
                pass

            elif user_name in private_sessions.keys() \
                    and (private_sessions.get(user_name)[1] == 'accepted request' or private_sessions.get(user_name)[1] == 'received public key and pq'
                         or private_sessions.get(user_name)[1] == 'received seed'):
                pass


            else:
                encrypted_message_from_client = my_funcs.receive_data(client_socket)
                #TODO : FIX THE PROBLEM FOR THE MSG FROM CLIENT, IT DOESN'T WORK WITHOUT THE CONDITIONS ELSE
                msg_from_client = decrypt_cipher(encrypted_message_from_client, client_seeds[client_socket][3]) # get the original message

                if user_name in private_sessions.keys():   # the user is in private session
                    if private_sessions[user_name][1] == 'initialized':   # need to answer to private session
                        print('**')
                        if msg_from_client == 'decline_p':
                            clients[private_sessions[user_name][0]].send(encrypt_msg(f'{user_name} declined to start a private session with you', client_seeds[clients[private_sessions[user_name][0]]][3]))
                            private_sessions.pop(user_name)
                            print("Private sessions keys : " + str(private_sessions.keys()))
                            print("Private sessions values : " + str(private_sessions.values()))
                        elif msg_from_client == 'confirm_p':
                            clients[private_sessions[user_name][0]].send(encrypt_msg(f'{user_name} confirmed to start a private session with you', client_seeds[clients[private_sessions[user_name][0]]][3]))
                            private_sessions[user_name][1] = 'accepted request'
                            clients[private_sessions[user_name][0]].send(encrypt_msg('creator_rsa', client_seeds[clients[private_sessions[user_name][0]]][3]))

                else:
                    if msg_from_client == '!private':  # trying to start private msg   # part 1
                        print('*')
                        enc_to_who = my_funcs.receive_data(client_socket)
                        to_who = decrypt_cipher(enc_to_who, client_seeds[client_socket][3])
                        print("The current username : " + user_name)
                        print("The to_who : " + to_who)
                        print("Clients keys : " + str(clients.keys()))

                        if to_who in clients.keys() and to_who != user_name:
                            if to_who in private_sessions.keys():
                                client_socket.send(encrypt_msg(f'ERROR: {to_who} already in private session',
                                                               client_seeds[client_socket][3]))
                            else:
                                private_sessions[to_who] = [user_name, 'initialized']
                                accept_to_private_session_msg = f'{user_name} wants to start a private session with you. (confirm_p/decline_p)'
                                clients[to_who].send(
                                    encrypt_msg(accept_to_private_session_msg, client_seeds[clients[to_who]][3]))
                                print("Private sessions keys : " + str(private_sessions.keys()))
                                print("Private sessions values : " + str(private_sessions.values()))
                        else:
                            if to_who == user_name:
                                client_socket.send(
                                    encrypt_msg(f'ERROR: you can not start a private session with yourself',
                                                client_seeds[client_socket][3]))
                            elif to_who in clients_users.keys():
                                client_socket.send(encrypt_msg(f'ERROR: the specific user you tried to reach is currently offline.',
                                                   client_seeds[client_socket][3]))
                            else:
                                client_socket.send(encrypt_msg(f'ERROR: there is no client called {to_who}',
                                                               client_seeds[client_socket][3]))


                    elif msg_from_client == '1': # exit from the program
                        client_socket.send(encrypt_msg('kill yourself', client_seeds[client_socket][3]))
                        clients.pop(user_name)
                        client_seeds.pop(client_socket)

                        # delete data from the database
                        delete_rec_from_client_seeds_table(str(client_socket))
                        delete_rec_from_client_socket_table(str(client_socket))

                        for others_clients in clients.values():
                            if others_clients is not client_socket:
                                if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                    enc_left_msg_to_others = encrypt_msg(f'{user_name} left the chat and became offline.', client_seeds[others_clients][3])
                                    others_clients.send(enc_left_msg_to_others)
                        break

                    elif msg_from_client == '***delete_account***':  # delete the account and exit
                        client_socket.send(encrypt_msg('kill yourself', client_seeds[client_socket][3]))

                        delete_rec_from_client_user_table(user_name)  # delete from db
                        delete_rec_from_client_seeds_table(str(client_socket))
                        delete_rec_from_client_socket_table(str(client_socket))
                        delete_rec_from_client_password_key_table(user_name)

                        clients.pop(user_name)
                        client_seeds.pop(client_socket)
                        clients_users.pop(user_name)

                        for others_clients in clients.values():
                            if others_clients is not client_socket:
                                if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                    enc_left_msg_to_others = encrypt_msg(f'{user_name} has left the session', client_seeds[others_clients][3])
                                    others_clients.send(enc_left_msg_to_others)
                        break

                    elif msg_from_client == '!online':  # show all the connected clients
                        online_clients = ' '.join(clients.keys())
                        client_socket.send(encrypt_msg(('All the current online clients:' + online_clients),
                                                       client_seeds[client_socket][3]))

                    elif msg_from_client == '!employers':  # show all the online employers
                        online_employers = show_only_employers_from_client_user()
                        online_employers_names = ' '.join([candidate[0] for candidate in online_employers if candidate[0] in clients.keys()])
                        client_socket.send(encrypt_msg(("All the current online employers are : " + online_employers_names),
                                                       client_seeds[client_socket][3]))

                    elif msg_from_client == '!candidates':  # show all the online candidates
                        online_candidates = show_only_candidates_from_client_user()
                        online_candidates_names = ' '.join([candidate[0] for candidate in online_candidates if candidate[0] in clients.keys()])
                        client_socket.send(encrypt_msg(("All the current online candidates are : " + online_candidates_names),
                                                       client_seeds[client_socket][3]))

                    elif msg_from_client == '!profile':  # show the first name and the last name for specific online client
                        enc_to_who = my_funcs.receive_data(client_socket)
                        to_who = decrypt_cipher(enc_to_who, client_seeds[client_socket][3])

                        online_clients = (' '.join(clients.keys())).split(' ')
                        online_employers = show_only_employers_from_client_user()
                        online_employers_usernames = [employer[0] for employer in online_employers]

                        if to_who not in clients_users:
                            string_to_send = f'ERROR: username {to_who} does not exist!'
                        else:
                            if to_who in online_clients:
                                string_to_send = f'\n\n{to_who} is {clients_users[to_who][3]}\nfirst name: {clients_users[to_who][0]}\nlast name: {clients_users[to_who][1]}'
                                if to_who in online_employers_usernames:
                                    string_to_send += f'\nworks at: {clients_users[to_who][5]}'
                            else:
                                string_to_send = f'{to_who} is currently offline.'

                        client_socket.send(encrypt_msg(string_to_send, client_seeds[client_socket][3]))

                    elif msg_from_client == 'WEBCAM':  # the user wants to open his camera
                        for others_clients in current_room.values():
                            if others_clients is not client_socket:
                                if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                    others_clients.send(encrypt_msg('start camera', client_seeds[others_clients][3]))
                                    others_clients.send(encrypt_msg(user_name, client_seeds[others_clients][3]))

                        encrypted_video_frame = my_funcs.receive_data(client_socket)
                        while encrypted_video_frame:
                            for others_clients in current_room.values():
                                if others_clients is not client_socket:
                                    if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                        others_clients.send(encrypted_video_frame)

                            encrypted_video_frame = my_funcs.receive_data(client_socket)

                    elif msg_from_client == 'FILE':  # the user wants to send a file
                        enc_file_name = my_funcs.receive_data(client_socket)
                        file_name = decrypt_cipher(enc_file_name, client_seeds[client_socket][3])

                        if file_name == 'File not accessible':  # the path of the file is invalid
                            continue

                        enc_file_name_hmac = my_funcs.receive_data(client_socket)
                        file_name_hmac = decrypt_cipher(enc_file_name_hmac, client_seeds[client_socket][3])

                        #TODO : CHANGE FOR MY HMAC
                        if hmac.new(str(client_seeds[client_socket][2]).encode(), file_name.encode(), hashlib.sha256).hexdigest() == file_name_hmac:    # check the integrity of the file name
                            f = open(f"server_temp_file.{file_name.split('.')[-1]}", "wb")

                            real_digest_maker = hmac.new(str(client_seeds[client_socket][2]).encode(), ''.encode(), hashlib.sha256)

                            encrypted_block_file = my_funcs.receive_data(client_socket)
                            block_file = decrypt_cipher_file(encrypted_block_file, client_seeds[client_socket][3])

                            while block_file != b'0': # get the file and write it to the temporary file
                                print('*')
                                f.write(block_file)
                                real_digest_maker.update(block_file)

                                encrypted_block_file = my_funcs.receive_data(client_socket)
                                block_file = decrypt_cipher_file(encrypted_block_file, client_seeds[client_socket][3])
                                print(block_file)

                            f.close()

                            real_digest = real_digest_maker.hexdigest()
                            print(f'hmac for the content in the file that sent {real_digest}')

                            enc_body_file_hmac = my_funcs.receive_data(client_socket)
                            body_file_hmac = decrypt_cipher(enc_body_file_hmac, client_seeds[client_socket][3])
                            print(f'hmac for the real file {body_file_hmac}')

                            if real_digest == body_file_hmac:    # check the integrity of the file body
                                print(f'The FILE sent from {user_name} is original')
                                for others_clients in current_room.values():
                                    if others_clients is not client_socket:
                                        if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                            others_clients.send(encrypt_msg('get file photo', client_seeds[others_clients][3]))
                                            time.sleep(0.5)
                                            others_clients.send(encrypt_msg(f'{user_name}_{os.path.basename(file_name)}', client_seeds[others_clients][3]))
                                time.sleep(0.1)

                                hmac_for_clients = {}
                                for others_clients in current_room.values():
                                    if others_clients is not client_socket:
                                        hmac_for_clients[others_clients] = hmac.new(str(client_seeds[others_clients][2]).encode(), ''.encode(), hashlib.sha256)

                                f = open(f"server_temp_file.{file_name.split('.')[-1]}", "rb")
                                block = f.read(1024)

                                while block:   # sending each file block to all the client in the room
                                    for others_clients in current_room.values():
                                        if others_clients is not client_socket:
                                            if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                                hmac_for_clients[others_clients].update(block)
                                                others_clients.send(encrypt_msg_file(block, client_seeds[others_clients][3]))
                                    time.sleep(0.1)

                                    block = f.read(1024)
                                f.close()

                                #os.remove("server_temp_file.txt")  # remove the temp file
                                os.remove(f"server_temp_file.{file_name.split('.')[-1]}")  # remove the temporary file we created
                                time.sleep(0.5)
                                for others_clients in current_room.values():
                                    if others_clients is not client_socket:
                                        if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                            others_clients.send(encrypt_msg_file(b'0', client_seeds[others_clients][3]))

                                time.sleep(0.1)
                                for others_clients in current_room.values():
                                    if others_clients is not client_socket:
                                        if others_clients not in [clients[c] for c in private_sessions.keys()] and others_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                            others_clients.send(encrypt_msg(hmac_for_clients[others_clients].hexdigest(), client_seeds[others_clients][3]))

                                hmac_for_clients.clear()

                            else:
                                print(f'Something change in the FILE sent from {user_name} 2')
                        else:
                            print(f'Something change in the FILE sent from {user_name} 1')

                    else:  # send any other message to all the clients in the room
                        msg_from_client_to_others = msg_header + msg_from_client
                        #for others_clients in current_room.values():
                        for other_clients in clients.values():
                            if other_clients is not client_socket:
                                if other_clients not in [clients[c] for c in private_sessions.keys()] and other_clients not in [clients[private_sessions[c][0]] for c in private_sessions.keys()]:
                                    other_clients.send(encrypt_msg(msg_from_client_to_others, client_seeds[other_clients][3]))



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create server socket
s.bind(('0.0.0.0', 23850))  # bind ip and port to socket
s.listen(20)  # set client queue to 10

# server is listening all the time!!!
while True:
    print('server is listening..')
    client_socket, address = s.accept()
    print(f'connection from {address} has been established')
    logging.info(f'connection from {address} has been established')

    t1 = threading.Thread(target=session_with_client, args=(client_socket,))
    t1.start()
