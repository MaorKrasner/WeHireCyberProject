import sqlite3

db = sqlite3.connect('chatDatabase.db', check_same_thread=False)

mycursor = db.cursor()


def insert_rec_to_client_user_table(user_name, first_name, last_name, encrypted_password, user_type):
    mycursor.execute('insert into client_user (user_name, first_name, last_name, encrypted_password, user_type) values (%s,%s,%s,%s,%s)',
                     (user_name, first_name, last_name, encrypted_password, user_type))
    db.commit()


def delete_rec_from_client_user_table(user_name_to_delete):
    mycursor.execute(f'''delete from client_user 
                         where user_name = "{user_name_to_delete}"''')
    db.commit()


def show_type_of_client_user(user_name):
    result = mycursor.execute(f'select user_type from client_user where user_name like "{user_name}"').fetchone()
    db.commit()
    return str(list(result)[0])


def show_password_of_specific_rec_client_user_table(user_name):
    result = mycursor.execute(f'select encrypted_password from client_user where user_name like "{user_name}"').fetchone()
    db.commit()
    return str(list(result)[0])


def insert_rec_to_client_password_key_table(user_name, password_key):
    mycursor.execute('insert into client_password_key (user_name, password_key) values (%s,%s)', (user_name, password_key))
    db.commit()


def delete_rec_from_client_password_key_table(user_name_to_delete):
    mycursor.execute(f'''delete from client_password_key 
                         where user_name = "{user_name_to_delete}"''')
    db.commit()


def show_key_of_specific_rec_client_password_key_table(user_name):
    result = mycursor.execute(f'select password_key from client_password_key where user_name like "{user_name}"').fetchone()
    db.commit()
    return str(list(result)[0])


def insert_rec_to_client_socket_table(username, client_socket):  # online clients
    mycursor.execute('insert into client (username, client_socket) values (%s,%s)', (username, client_socket))
    db.commit()


def delete_rec_from_client_socket_table(client_socket_to_delete):
    mycursor.execute(f'''delete from client 
                         where client_socket = "{client_socket_to_delete}"''')
    db.commit()


def insert_rec_to_client_seeds_table(client_socket, public_key, modulo_pq, seed, setSeed_pad):  # online clients
    mycursor.execute('insert into client_seeds (client_socket, public_key, modulo_pq, seed, setSeed_pad) values (%s,%s,%s,%s,%s)',
                     (client_socket, public_key, modulo_pq, seed, setSeed_pad))
    db.commit()


def delete_rec_from_client_seeds_table(client_socket_to_delete):
    mycursor.execute(f'''delete from client_seeds 
                         where client_socket = "{client_socket_to_delete}"''')
    db.commit()


def insert_data_from_db_to_clients_users(clients_users):
    mycursor.execute('select * from client_user')
    for rec in mycursor:
        clients_users[rec[0]] = [rec[1], rec[2], rec[3], rec[4]]  # (user_name, first_name, last_name, password, user_type)


if __name__ == '__main__':
    table = """CREATE TABLE client_password_key
        (user_name VARCHAR(255) PRIMARY KEY NOT NULL,
        password_key VARCHAR(255) NOT NULL
        );"""

    mycursor.execute(table)
    #mycursor.execute("DROP TABLE client_user")
    db.commit()