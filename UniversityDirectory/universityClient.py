import socket

HOST_IP_ADDRESS = "127.0.0.1"
PORT_NUMBER = 55555

if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST_IP_ADDRESS, PORT_NUMBER))
    except socket.error as e:
        print(str(e))
    print("Connected to server")

    client_socket.send("Maor".encode())
    data = client_socket.recv(1024).decode()
    print("The server sent : " + data)

    client_socket.close()