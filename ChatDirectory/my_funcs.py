import decimal
import math
from decimal import *


def receive_data_with_decode(sock):  # Receive the message
    data = b''
    while True:
        part = sock.recv(4096)
        data += part
        if len(part) < 4096:
            # either 0 or end of data
            break
    return data.decode()


def receive_data(sock):  # Receive the message without decode()
    data = b''
    while True:
        #try:
        #    part = sock.recv(BUFF_SIZE)
        #except:
        #    return -999

        part = sock.recv(4096)  # problem here!!!
        data += part
        if len(part) < 4096:
            # either 0 or end of data
            break
    return data


def is_prime(number):
    if number == 2:
        return True
    if number % 2 == 0 or number <= 1:
        return False

    sqr = int(math.sqrt(number)) + 1

    for divisor in range(3, sqr, 2):
        if number % divisor == 0:
            return False
    return True


def key_exchange(clientsocket, p, q, x):  # all numbers
    if not is_prime(p) or not is_prime(q):
        raise ValueError('P or Q were not prime')

    eq = (p - 1) * (q - 1) + 1

    y = 1
    xy = x * y

    while xy != eq:
        x += 1
        y = eq / x
        xy = x * y

    print("public key, x: " + str(x))
    print("private key, y: " + str(y))
    print("modulo (pq): " + str(p * q))


def rsa_encryption_decryption(pq, key, msg):
    exp = int(((msg ** int(key)) * (msg ** (key - int(key)))) % pq)
    encrypted_message = exp
    # print('Your de/encrypted message is: ' + str(encrypted_message))
    return encrypted_message


def to_ascii(text):
    ascii_values = [ord(character) for character in text]
    return ascii_values


def add_element_in_tuple(t, i, num):
    ll = list(t)
    ll.append(num)
    t = tuple(ll)
    return t

if __name__ == '__main__':
    count = 0
    for i in range(100, 1000):
        if is_prime(i):
            print(str(i) + "is prime")
            count += 1
    print(count)