import os
import sqlite3
from UniversityDirectory import my_hmac_functions

conn = sqlite3.connect('C://Users//maork//OneDrive//Desktop//WeHireCyberProject//UniversityDirectory//UniversityDatabase.db', check_same_thread=False)

cursor = conn.cursor()

# university_directory_path = "/Users/maorkrasner/Desktop/WeHireCyberProject/UniversityStudentsDiplomasFolder/"  # FOR MAC
university_directory_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + "\\UniversityStudentsDiplomasFolder" + "\\"


def insert_row_into_table_uni(table_name, values_tuple):
    command = "INSERT INTO " + table_name + " " + "VALUES " + str(values_tuple)
    cursor.execute(command)
    conn.commit()


def print_all_rows_in_table_uni(table_name):
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


def find_student_in_students_table_uni(id_of_student):
    find_student_query = "SELECT ID FROM students WHERE ID = " + str(id_of_student) + ";"
    student_query_result = cursor.execute(find_student_query).fetchone()
    conn.commit()
    return student_query_result is not None


def find_signing_key_for_diploma_uni(id_of_student):
    if not find_student_in_students_table_uni(id_of_student):
        return "0"

    find_key_query = "SELECT Signing_key FROM certificates WHERE Student_ID = " + str(id_of_student) + ";"
    find_key_query_result = cursor.execute(find_key_query).fetchone()
    conn.commit()
    return str(find_key_query_result)


def find_signed_file_name_uni(id_of_student):
    file_name_query = "SELECT Signed_file_name FROM certificates WHERE Student_ID = " + str(id_of_student) + ";"
    file_name_query_result = cursor.execute(file_name_query).fetchone()
    conn.commit()
    return str(list(file_name_query_result)[0])


def create_and_sign_diploma(person_id, signing_key):
    if not find_student_in_students_table_uni(person_id):
        return False, "Text with nothing in it"

    find_student_name_query = "SELECT First ||' '|| Last FROM students WHERE ID = " + str(person_id) + ";"
    name_query_res = cursor.execute(find_student_name_query).fetchone()

    path_to_check_if_diploma_already_exists = university_directory_path + str(name_query_res[0]) + " " + str(person_id) + ".txt"

    # means the student already got the diploma from the university and there is no need to sign it again, just to send true and the content
    if os.path.exists(path_to_check_if_diploma_already_exists):
        with open(path_to_check_if_diploma_already_exists, 'r') as f:
            txt_file_content = f.read()
        f.close()

        return True, txt_file_content

    find_grades_for_courses_query = """SELECT subjects.Subject_name, grades.grade
                                        FROM subjects INNER JOIN (grades INNER JOIN students ON grades.Student_ID = students.ID) 
                                        ON subjects.Subject_ID = grades.Subject_ID 
                                        WHERE students.ID = """ + str(person_id) + ";"
    grades_for_courses_list = cursor.execute(find_grades_for_courses_query).fetchall()

    grades_for_courses_list.insert(0, name_query_res)

    text_file_path = university_directory_path + str(name_query_res[0]) + " " + str(person_id) + ".txt"

    pdf_text_to_enter = ""
    pdf_text_to_enter += "University of Tel Aviv\n\n"
    pdf_text_to_enter += f'Student name : {name_query_res[0]}\n'
    pdf_text_to_enter += f'Student ID : {person_id}'
    pdf_text_to_enter += f'\n\n\n-------------------- GRADES --------------------\n\n\n'
    for i in range(1, len(grades_for_courses_list)):
        pdf_text_to_enter +=f'{grades_for_courses_list[i][0]} : {grades_for_courses_list[i][1]}\n'

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

    insert_row_into_table_uni("certificates", (person_id, str(text_file_path.split(sign_to_split_with)[-1]), str(text_file_sign_digest.hex()), signing_key))

    with open(text_file_path, 'r') as file_to_send:
        message_to_send = file_to_send.read()
    file_to_send.close()

    return True, message_to_send

def verify_integrity_of_certificate(id_of_student, message_that_student_passed):
    if not find_student_in_students_table_uni(id_of_student):
        return False

    info_about_student = "SELECT Signed_file_digest, Signing_key from certificates WHERE Student_ID = " + str(id_of_student) + ";"
    info_query_result = cursor.execute(info_about_student).fetchone()

    original_file_digest = str(info_query_result[0])
    print(original_file_digest)

    signing_key = str(info_query_result[1]).encode()
    print(str(info_query_result[1]))

    digest_of_file_student_passed = my_hmac_functions.hmac_sign_with_sha256(signing_key, message_that_student_passed)
    print(str(digest_of_file_student_passed.hex()))

    print("RESULT NEEDS TO BE : " + str(original_file_digest == str(digest_of_file_student_passed.hex())))

    return original_file_digest == str(digest_of_file_student_passed.hex())

def close_connection_uni():
    conn.close()