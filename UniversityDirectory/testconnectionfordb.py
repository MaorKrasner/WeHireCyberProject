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
    command = "SELECT ID FROM students WHERE ID = " + str(id_of_student) + ";"
    result = cursor.execute(command).fetchone()
    if result is None:
        return False
    #find_grades_command = "SELECT subjects.Subject_name, grades.grade"


def close_connection():
    conn.close()


if __name__ == '__main__':
    #cursor.execute("DROP TABLE IF EXISTS grades")
    #table = """CREATE TABLE grades
    #        (Subject_ID VARCHAR(25) NOT NULL,
    #        Student_ID VARCHAR(255) NOT NULL,
    #        grade INT CHECK(grade>0) NOT NULL
    #        );"""

    #cursor.execute(table)
    #cmd = "ALTER TABLE grades DROP INDEX reference_unique;"
    #cursor.execute(cmd)
    #conn.commit()
    #insert_row_into_table("students", (213225576, "Maor", "Krasner"))
    #print_all_rows_in_table("students")
    val = create_diploma_and_sign_it(213225576)
    print(val)

    #cursor.execute("DELETE FROM grades")
    #conn.commit()

    #insert_row_into_table("grades", (1, 213225576, 100))
    #insert_row_into_table("grades", (2, 213225577, 90))
    #insert_row_into_table("grades", (3, 213225578, 95))
    #insert_row_into_table("grades", (1, 213225579, 85))
    #insert_row_into_table("grades", (2, 213225576, 100))
   # conn.commit()
