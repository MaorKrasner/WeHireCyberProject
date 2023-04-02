import os
import sqlite3
import fileconvertor
import hmacfunctions

conn = sqlite3.connect('UniversityDatabase.txt')

cursor = conn.cursor()

university_directory_path = "C:\\Users\\maork\\OneDrive\\Desktop\\WeHireCyberProject\\UniversityStudentsDiplomasFolder\\"


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


def create_diploma_and_sign_it(id_of_student):
    if not find_student_in_students_table(id_of_student):
        return False

    find_grades_for_courses_query = """SELECT subjects.Subject_name, grades.grade
                                    FROM subjects INNER JOIN (grades INNER JOIN students ON grades.Student_ID = students.ID) 
                                    ON subjects.Subject_ID = grades.Subject_ID 
                                    WHERE students.ID = """ + str(id_of_student) + ";"
    grades_for_courses_list = cursor.execute(find_grades_for_courses_query).fetchall()

    find_student_name_query = "SELECT First ||' '|| Last FROM students WHERE ID = " + str(id_of_student) + ";"
    name_query_res = cursor.execute(find_student_name_query).fetchone()

    grades_for_courses_list.insert(0, name_query_res)

    text_file_path = university_directory_path + str(name_query_res[0]) + " " + str(id_of_student) + ".txt"
    pdf_file_path = university_directory_path + str(name_query_res[0]) + " " + str(id_of_student) + ".pdf"

    with open(text_file_path, 'w') as f:
        f.write("University Of Tel Aviv\n\n")
        f.write("Student's full name : " + str(name_query_res[0]) + "\n\n")
        f.write("Student's ID : " + str(id_of_student))
        f.write("\n\n\n-----  GRADES  -----\n\n\n")
        for i in range(1, len(grades_for_courses_list)):
            f.write(str(grades_for_courses_list[i][0]) + " : " + str(grades_for_courses_list[i][1]) + "\n")

    fileconvertor.convert_from_text_to_pdf(text_file_path, pdf_file_path)
    f.close()

    os.remove(text_file_path)

    key = "secretkey0123456789".encode()

    with open(pdf_file_path, 'rb') as pdf_file_to_sign:
        message_to_sign = pdf_file_to_sign.read()

    pdf_file_sign_digest = hmacfunctions.hmac_sign_with_sha256(key, message_to_sign)

    print("file digest/tag = " + str(pdf_file_sign_digest.hex()))

    insert_row_into_table("certificates", (id_of_student, str(pdf_file_path.split("\\")[-1]), str(pdf_file_sign_digest.hex()), key.decode()))

    return True


def verify_if_the_certificate_is_real(id_of_student, message_that_student_passed):
    if not find_student_in_students_table(id_of_student):
        return False

    info_about_student = "SELECT Signed_file_digest, Signing_key from certificates WHERE Student_ID = " + str(id_of_student) + ";"
    info_query_result = cursor.execute(info_about_student).fetchone()

    original_file_digest = str(info_query_result[0])
    print(original_file_digest)

    signing_key = str(info_query_result[1]).encode()
    print(str(info_query_result[1]))

    digest_of_file_student_passed = hmacfunctions.hmac_sign_with_sha256(signing_key, message_that_student_passed)

    return original_file_digest == str(digest_of_file_student_passed.hex())


def close_connection():
    conn.close()


if __name__ == '__main__':
     #cursor.execute("DROP TABLE IF EXISTS certificates")
     #table = """CREATE TABLE certificates
     #       (Student_ID VARCHAR(25) PRIMARY KEY NOT NULL,
     #       Signed_file_name VARCHAR(255) NOT NULL,
     #       Signed_file_digest VARCHAR(255)  NOT NULL,
     #       Signing_key VARCHAR(255) NOT NULL
     #       );"""

     #cursor.execute(table)
    # cmd = "ALTER TABLE grades DROP INDEX reference_unique;"
    # cursor.execute(cmd)
     #conn.commit()
    # insert_row_into_table("students", (213225577, "Tom", "Yanover"))
    # insert_row_into_table("students", (213225578, "Yan", "Vayner"))
    # insert_row_into_table("students", (213225579, "Ofek", "Bassan"))
    # insert_row_into_table("students", (213225580, "Michal", "Shammai"))
    # print_all_rows_in_table("students")

    current_student_id = 213225576

    #val = create_diploma_and_sign_it(current_student_id)
    #print(val)

    signed_file_name_query = "SELECT Signed_file_name from certificates WHERE Student_ID = " + str(current_student_id) + ";"
    signed_file_name_query_result = cursor.execute(signed_file_name_query).fetchall()

    #file_path_to_check = university_directory_path + str(signed_file_name_query_result[0][0])
    file_path_to_check = "C:\\Users\\maork\\OneDrive\\Desktop\\Maor Krasner 213225576 diploma.pdf"

    with open(file_path_to_check, "rb") as f_to_check:
        message_to_check = f_to_check.read()
        print(str(message_to_check))

    print(verify_if_the_certificate_is_real(current_student_id, message_to_check))

    #cursor.execute("DELETE FROM certificates")
    #conn.commit()

     #insert_row_into_table("grades", (10, 213225576, 85))
     #insert_row_into_table("grades", (8, 213225577, 90))
     #insert_row_into_table("grades", (11, 213225578, 95))
     #insert_row_into_table("grades", (5, 213225579, 85))
     #insert_row_into_table("grades", (4, 213225580, 97))
     #insert_row_into_table("grades", (11, 213225576, 93))
    # insert_row_into_table("subjects", (6, "Operating systems"))
    # insert_row_into_table("subjects", (7, "Real time programming"))
    # insert_row_into_table("subjects", (8, "Low level programming in C and Assembly"))
    # insert_row_into_table("subjects", (9, "Object Oriented Programming"))
    # insert_row_into_table("subjects", (10, "Programming in python"))
    # insert_row_into_table("subjects", (11, "Databases and SQL"))
    # conn.commit()
