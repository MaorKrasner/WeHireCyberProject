import sqlite3

conn = sqlite3.connect('UniversityDatabase.txt')

cursor = conn.cursor()

'''
table = """CREATE TABLE certificates
        (Student_ID VARCHAR(25) PRIMARY KEY NOT NULL,
        Sign_digest VARCHAR(255) NOT NULL,
        Signed_file_name VARCHAR(255) NOT NULL);"""

cursor.execute(table)
'''

def insert_row_into_table(table_name, values_tuple):
    command = "INSERT INTO " + table_name + " " + "VALUES " + str(values_tuple)
    cursor.execute(command)
    conn.commit()

def print_all_rows_in_table(table_name):
    select_query_command = """SELECT * from """ + table_name
    cursor.execute(select_query_command)
    rows = cursor.fetchall()
    print("Total rows are:  ", len(rows))
    print("Printing each row")
    for row in rows:
        for col in row:
            print(col, end=' ')
        print()
    conn.commit()


def create_diploma_and_sign_it(id_of_student):
    command = """IF EXISTS (SELECT * FROM Products WHERE ID = ?)"""
    result = cursor.execute(command, id_of_student)
    if result is None:
        return False
    return True

def close_connection():
    conn.close()


if __name__ == '__main__':
    #insert_row_into_table("students", (213225576, "Maor", "Krasner"))
    #print_all_rows_in_table("students")
    val = create_diploma_and_sign_it(213225576)
    print(val)
