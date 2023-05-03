import socket
import string
import random
from university_database_management import *
from ChatDirectory.my_funcs import *

PORT_NUMBER = 2358


def create_random_key(n):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=n))


if __name__ == '__main__':
    # TODO : IN C MODE, WHEN THERE IS ALREADY DIPLOMA, CHECK WHY IT ADDS (cid:10)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(("127.0.0.1", 2358))
    except socket.error as e:
        print(str(e))
    print("Connected to server")

    status_of_person = input("Enter e if you are an employer, Enter c if you are candidate : ")
    while status_of_person != "c" and status_of_person != "e":
        status_of_person = input("Enter e if you are an employer, Enter c if you are candidate : ")

    client_socket.send(status_of_person.encode())
    answer = client_socket.recv(1024).decode()
    print(answer)

    if status_of_person == "c":
        id_of_candidate = input("Enter your ID : ")
        key_to_sign_file_with = create_random_key(random.randint(16, 128))
        print("Key is : " + key_to_sign_file_with)
        client_socket.send((id_of_candidate + " " + key_to_sign_file_with).encode())

        #signed_file_content = recvall_with_decode(client_socket)
        signed_file_content = receive_data(client_socket)

        if signed_file_content != "ID of student didn't show up in the database of the university!":
            print(signed_file_content)
            documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            print(documents_path)

            sign_of_path = "/" if documents_path.__contains__("/") else "\\"
            full_diploma_path_pdf = documents_path + sign_of_path + find_signed_file_name(id_of_candidate)
            full_diploma_path_text = full_diploma_path_pdf.replace(".pdf", ".txt")
            print(full_diploma_path_pdf)
            print(full_diploma_path_text)

            #with open(full_diploma_path_pdf, 'w', encoding="utf8") as f:
            #    f.write(signed_file_content)
            #f.close()

            #with open(full_diploma_path_text, 'w') as f:
            #    f.write(signed_file_content)
            #f.close()

            with open(full_diploma_path_text, 'wb') as f:
                f.write(signed_file_content)
            f.close()

            fileconvertor.convert_from_text_to_pdf(full_diploma_path_text, full_diploma_path_pdf)
            #fileconvertor.convert_from_text_to_pdf_pypdf4(full_diploma_path_text, full_diploma_path_pdf)
            os.remove(full_diploma_path_text)



            print("I saved for you the file in : " + documents_path)
        else:
            print(signed_file_content)

    else:
        id_of_candidate = input("Enter the student's ID : ")
        client_socket.send(id_of_candidate.encode())
        response_for_id = client_socket.recv(1024).decode()
        print(response_for_id)

        message_path = input("Enter the full path of the file that the student passed you : ")
        while not os.path.exists(message_path):
            print("Path invalid ! Try again.")
            message_path = input("Enter the full path of the file that the student passed you : ")
        print("Path valid.")

        with open(message_path, 'rb') as file_to_check:
            message_of_file_to_check = file_to_check.read()
        #message_of_file_to_check = ''.join(message_of_file_to_check.replace("\n", ""))

        client_socket.send(message_of_file_to_check)
        status_response = client_socket.recv(1024).decode()
        print(status_response)

    client_socket.close()
