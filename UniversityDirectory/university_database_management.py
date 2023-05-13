import os
import sqlite3
import pdfreader

from UniversityDirectory import my_hmac_functions
from UniversityDirectory.file_convertor import *
import textwrap

conn = sqlite3.connect('UniversityDatabase.db', check_same_thread=False)

cursor = conn.cursor()

# university_directory_path = "/Users/maorkrasner/Desktop/WeHireCyberProject/UniversityStudentsDiplomasFolder/"
university_directory_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + "\\UniversityStudentsDiplomasFolder" + "\\"


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


def find_student_in_students_table(id_of_student):
    find_student_query = "SELECT ID FROM students WHERE ID = " + str(id_of_student) + ";"
    student_query_result = cursor.execute(find_student_query).fetchone()
    conn.commit()
    return student_query_result is not None


def find_signing_key_for_diploma(id_of_student):
    if not find_student_in_students_table(id_of_student):
        return "0"

    find_key_query = "SELECT Signing_key FROM certificates WHERE Student_ID = " + str(id_of_student) + ";"
    find_key_query_result = cursor.execute(find_key_query).fetchone()
    conn.commit()
    return str(find_key_query_result)


def find_signed_file_name(id_of_student):
    file_name_query = "SELECT Signed_file_name FROM certificates WHERE Student_ID = " + str(id_of_student) + ";"
    file_name_query_result = cursor.execute(file_name_query).fetchone()
    conn.commit()
    return str(list(file_name_query_result)[0])


def create_and_sign_diploma(person_id, signing_key):
    if not find_student_in_students_table(person_id):
        return False, "Text with nothing in it"

    find_student_name_query = "SELECT First ||' '|| Last FROM students WHERE ID = " + str(person_id) + ";"
    name_query_res = cursor.execute(find_student_name_query).fetchone()

    path_to_check_if_diploma_already_exists = university_directory_path + str(name_query_res[0]) + " " + str(person_id) + ".txt"

    # means the student already got the diploma from the university and there is no need to sign it again,
    # just to send true and the content
    if os.path.exists(path_to_check_if_diploma_already_exists):
        with open(path_to_check_if_diploma_already_exists, 'rb') as f:
            pdf_file_content = f.read()
        f.close()

        return True, pdf_file_content

    find_grades_for_courses_query = """SELECT subjects.Subject_name, grades.grade
                                        FROM subjects INNER JOIN (grades INNER JOIN students ON grades.Student_ID = students.ID) 
                                        ON subjects.Subject_ID = grades.Subject_ID 
                                        WHERE students.ID = """ + str(person_id) + ";"
    grades_for_courses_list = cursor.execute(find_grades_for_courses_query).fetchall()

    grades_for_courses_list.insert(0, name_query_res)

    text_file_path = university_directory_path + str(name_query_res[0]) + " " + str(person_id) + ".txt"

    pdf_text_to_enter = ""
    pdf_text_to_enter += "University of Tel Aviv\r\n\r\n"
    pdf_text_to_enter += f'Student name : {name_query_res[0]}\r\n'
    pdf_text_to_enter += f'Student ID : {person_id}'
    pdf_text_to_enter += f'\r\n\r\n\r\n-------------------- GRADES --------------------\r\n\r\n\r\n'
    for i in range(1, len(grades_for_courses_list)):
        pdf_text_to_enter +=f'{grades_for_courses_list[i][0]} : {grades_for_courses_list[i][1]}\r\n'

    with open(text_file_path, 'wb') as f:
        f.write(pdf_text_to_enter.encode())

    f.close()

    with open(text_file_path, 'rb') as f:
        text_to_sign = f.read()
        print(text_to_sign)
    f.close()

    text_file_sign_digest = my_hmac_functions.hmac_sign_with_sha256(signing_key.encode(), text_to_sign)

    print("file digest/tag = " + str(text_file_sign_digest.hex()))

    sign_to_split_with = "/" if str(text_file_path).__contains__("/") else "\\"

    insert_row_into_table("certificates", (person_id, str(text_file_path.split(sign_to_split_with)[-1]), str(text_file_sign_digest.hex()), signing_key))

    with open(text_file_path, 'rb') as file_to_send:
        message_to_send = file_to_send.read()
    file_to_send.close()

    return True, message_to_send

def verify_integrity_of_certificate(id_of_student, message_that_student_passed):
    if not find_student_in_students_table(id_of_student):
        return False

    info_about_student = "SELECT Signed_file_digest, Signing_key from certificates WHERE Student_ID = " + str(id_of_student) + ";"
    info_query_result = cursor.execute(info_about_student).fetchone()

    original_file_digest = str(info_query_result[0])
    print(original_file_digest)

    signing_key = str(info_query_result[1]).encode()
    print(str(info_query_result[1]))

    digest_of_file_student_passed = my_hmac_functions.hmac_sign_with_sha256(signing_key, message_that_student_passed)
    print(str(digest_of_file_student_passed.hex()))

    return original_file_digest == str(digest_of_file_student_passed.hex())


def close_connection():
    conn.close()


if __name__ == '__main__':
    #cursor.execute("DELETE FROM certificates")
    #conn.commit()

    create_and_sign_diploma(213225576, 'asdhuaisnduians')

    #create_and_sign_diploma(213225576, "uashdiy31231273tybd")
    # cursor.execute("DROP TABLE IF EXISTS certificates")
    # table = """CREATE TABLE certificates
    #       (Student_ID VARCHAR(25) PRIMARY KEY NOT NULL,
    #       Signed_file_name VARCHAR(255) NOT NULL,
    #       Signed_file_digest VARCHAR(255)  NOT NULL,
    #       Signing_key VARCHAR(255) NOT NULL
    #       );"""

    # cursor.execute(table)
    # cmd = "ALTER TABLE grades DROP INDEX reference_unique;"
    # cursor.execute(cmd)
    # conn.commit()
    # insert_row_into_table("students", (213225577, "Tom", "Yanover"))
    # insert_row_into_table("students", (213225578, "Yan", "Vayner"))
    # insert_row_into_table("students", (213225579, "Ofek", "Bassan"))
    # insert_row_into_table("students", (213225580, "Michal", "Shammai"))
    # print_all_rows_in_table("students")



    current_student_id = 213225576

    # cursor.execute("DELETE FROM certificates WHERE Student_ID = " + str(current_student_id))

    #cursor.execute("DELETE FROM certificates")
    #conn.commit()

    # created_or_sent_successfully, pdf_file_content = create_diploma_and_sign_it(current_student_id)
    # print(created_or_sent_successfully)

    signed_file_name_query = "SELECT Signed_file_name from certificates WHERE Student_ID = " + str(current_student_id) + ";"
    signed_file_name_query_result = cursor.execute(signed_file_name_query).fetchall()

    file_path_to_check = 'C://Users//maork//OneDrive//Desktop//newmaor.txt'
    print(os.path.exists(file_path_to_check))
    #file_path_to_check = university_directory_path + str(signed_file_name_query_result[0][0])
    #file_path_to_check = "/Users/maorkrasner/Desktop/Tom Yanover 213225577.txt"

    with open(file_path_to_check, 'rb') as f_to_check:
        message_to_check = f_to_check.read()
        print(str(message_to_check))
    f_to_check.close()

    with open("C://Users//maork//OneDrive//Desktop//WeHireCyberProject//UniversityStudentsDiplomasFolder//Maor Krasner 213225576.txt", 'rb') as f:
        msg = f.read()
        print(msg)
    f.close()


    print(verify_integrity_of_certificate(current_student_id, message_to_check))

    # cursor.execute("DELETE FROM certificates")
    # conn.commit()

    # insert_row_into_table("grades", (10, 213225576, 85))
    # insert_row_into_table("grades", (5, 213225577, 95))
    # insert_row_into_table("grades", (11, 213225577, 95))
    # insert_row_into_table("grades", (3, 213225577, 95))

    # insert_row_into_table("grades", (11, 213225578, 95))
    # insert_row_into_table("grades", (5, 213225579, 85))
    # insert_row_into_table("grades", (4, 213225580, 97))
    # insert_row_into_table("grades", (11, 213225576, 93))
    # insert_row_into_table("subjects", (6, "Operating systems"))
    # insert_row_into_table("subjects", (7, "Real time programming"))
    # insert_row_into_table("subjects", (8, "Low level programming in C and Assembly"))
    # insert_row_into_table("subjects", (9, "Object Oriented Programming"))
    # insert_row_into_table("subjects", (10, "Programming in python"))
    # insert_row_into_table("subjects", (11, "Databases and SQL"))

    # conn.commit()
