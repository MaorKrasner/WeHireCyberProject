import sqlite3

db = sqlite3.connect('chatDatabase.db', check_same_thread=False)

my_cursor = db.cursor()


def insert_row_into_table(table_name, values_tuple):
    command = "INSERT INTO " + table_name + " " + "VALUES " + str(values_tuple)
    my_cursor.execute(command)
    db.commit()


def insert_rec_to_client_user_table(user_name, first_name, last_name, encrypted_password, user_type, user_ID, company_name):
    my_cursor.execute('insert into client_user (user_name, first_name, last_name, encrypted_password, user_type, user_ID, company_name) values (%s,%s,%s,%s,%s,%s,%s)',
                      (user_name, first_name, last_name, encrypted_password, user_type, user_ID, company_name))
    db.commit()


def delete_rec_from_client_user_table(user_name_to_delete):
    my_cursor.execute(f'''delete from client_user 
                         where user_name = "{user_name_to_delete}"''')
    db.commit()


def show_type_of_client_user(user_name):
    result = my_cursor.execute(f'select user_type from client_user where user_name like "{user_name}"').fetchone()
    db.commit()
    return str(list(result)[0])


def show_password_of_specific_rec_client_user_table(user_name):
    result = my_cursor.execute(f'select encrypted_password from client_user where user_name like "{user_name}"').fetchone()
    db.commit()
    return str(list(result)[0])


def insert_rec_to_client_password_key_table(user_name, password_key):
    my_cursor.execute('insert into client_password_key (user_name, password_key) values (%s,%s)', (user_name, password_key))
    db.commit()


def delete_rec_from_client_password_key_table(user_name_to_delete):
    my_cursor.execute(f'''delete from client_password_key 
                         where user_name = "{user_name_to_delete}"''')
    db.commit()


def show_key_of_specific_rec_client_password_key_table(user_name):
    result = my_cursor.execute(f'select password_key from client_password_key where user_name like "{user_name}"').fetchone()
    db.commit()
    return str(list(result)[0])


def insert_rec_to_client_socket_table(username, client_socket):  # online clients
    my_cursor.execute('insert into client (username, client_socket) values (%s,%s)', (username, client_socket))
    db.commit()


def delete_rec_from_client_socket_table(client_socket_to_delete):
    my_cursor.execute(f'''delete from client 
                         where client_socket = "{client_socket_to_delete}"''')
    db.commit()


def insert_rec_to_client_seeds_table(client_socket, public_key, modulo_pq, seed, setSeed_pad):  # online clients
    my_cursor.execute('insert into client_seeds (client_socket, public_key, modulo_pq, seed, setSeed_pad) values (%s,%s,%s,%s,%s)',
                      (client_socket, public_key, modulo_pq, seed, setSeed_pad))
    db.commit()


def delete_rec_from_client_seeds_table(client_socket_to_delete):
    my_cursor.execute(f'''delete from client_seeds 
                         where client_socket = "{client_socket_to_delete}"''')
    db.commit()


def insert_data_from_db_to_clients_users(clients_users):
    my_cursor.execute('select * from client_user')
    for rec in my_cursor:
        clients_users[rec[0]] = [rec[1], rec[2], rec[3], rec[4], rec[5], rec[6]]  # (user_name, first_name, last_name, password, user_type, user_ID, company_name)


def show_only_employers_from_client_user():
    result_list = my_cursor.execute(f'select user_name, first_name, last_name, company_name from client_user where user_type like "employer"').fetchall()
    db.commit()
    return result_list


def show_only_candidates_from_client_user():
    result_list = my_cursor.execute(f'select user_name, first_name, last_name, user_ID from client_user where user_type like "candidate"').fetchall()
    db.commit()
    return result_list


if __name__ == '__main__':
    #table = """CREATE TABLE client_password_key
    #    (user_name VARCHAR(255) PRIMARY KEY NOT NULL,
    #    password_key VARCHAR(255) NOT NULL
    #    );"""

    #table = """ALTER TABLE client_user ADD company_name VARCHAR(255) NOT NULL"""

    #my_cursor.execute(table)
    #mycursor.execute("DROP TABLE client_user")

    #insert_row_into_table("client_user", ("maorkr", "Maor", "Krasner", "asdashdihas", "candidate", "213225576", "clum"))
    #insert_row_into_table("client_user", ("maormanager", "Mark", "Kras", "asdasasdasdihas", "employer", "0", "WeHireCyber"))
    insert_row_into_table("client_user",
                          ("tomyan", "Tom", "Yanover", "djnhaasdhajs", "employer", "0", "Intel LTD"))

    #client_usrs = {}

    #insert_data_from_db_to_clients_users(client_usrs)
    #print(client_usrs)

    #my_cursor.execute("delete from client_user")

    db.commit()