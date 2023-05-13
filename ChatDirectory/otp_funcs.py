import random


class SetSeed:
    def __init__(self, seed, a, b):
        self.start_seed = seed
        self.A = a
        self.B = b
        # print(self.A)
        # print(self.B)

    def print_p(self):
        print(self.start_seed)

    def my_random_pad_generator(self, a, b, len_key, final_key):
        while len_key != 0:
            #print ("a : " + str(a))
            #print("start seed : " + str(self.start_seed))
            a_s = int((str(a) + str(self.start_seed))+(str(a) + str(self.start_seed))[4])  # string index out of range
            #print(a_s)
            self.start_seed = (a_s + b) % (2 ** 32)
            if (self.start_seed % 2) == 0:
                final_key.append(format(1, 'b'))
            else:
                final_key.append(format(0, 'b'))
            len_key = len_key - 1
        return final_key

    def my_key_stream_create_pad(self, key_len):
        pad = ''.join(self.my_random_pad_generator(self.A, self.B, key_len, []))
        # print(f'pad: {pad}')
        #pad = ''.join(self.my_random_LCD(self.A, self.B, key_len, []))
        return pad


    def my_random_LCD(self, a, b, len_key, final_key):
            if len_key == 0:
                return final_key
            a_s = int(str(a) + str(self.start_seed))  # RecursionError: maximum recursion depth exceeded while getting the str of an object
            self.start_seed = (a_s + b) % (2 ** 32)
            if (self.start_seed % 2) == 0:
                final_key.append(format(1, 'b'))
            else:
                final_key.append(format(0, 'b'))
            return self.my_random_LCD(a, b, len_key - 1, final_key)




def text_to_byte(txt):
    return ''.join([(format(ord(c), 'b')).zfill(8) for c in txt])


def byte_to_text(inp):
    (blob, chunck_size) = len(inp), 8
    byte_list = [inp[i:i+chunck_size] for i in range(0, blob, chunck_size)]
    return ''.join([chr(int(i, 2)) for i in byte_list])


def key_stream(key_len):
    return ''.join([format(random.randint(0, 1), 'b') for a in range(key_len)])


def my_random_LCD(a, b, s, len_key, final_key):
    if len_key == 0:
        return final_key
    a_s = int(str(a) + str(s))
    new_s = (a_s + b) % (2**32)
    if (new_s % 2) == 0:
        final_key.append(format(1, 'b'))
    else:
        final_key.append(format(0, 'b'))
    return my_random_LCD(a, b, new_s, len_key-1, final_key)


def my_key_stream_create_pad(key_len, seed):
    return ''.join(my_random_LCD(8888, 9999, seed, key_len, []))


def my_key_stream(key_len, seed):
    return ''.join(my_random_LCD(random.randint(1, 9999999), random.randint(1, 9999999), seed, key_len, []))


def encrypt(bin_txt, bin_pad):
    return bytes([int(_a) ^ int(_b) for _a, _b in zip(bin_txt, bin_pad)])

def decrypt(cipher_txt, bin_pad):
    return bytes([int(_a) ^ int(_b) for _a, _b in zip(cipher_txt, bin_pad)])


def main():
    while True:
        msg = input('enter msg:')
        msg_bin = text_to_byte(msg)
        print('msg_bin: ', msg_bin)
        print(len(msg_bin))
        # pad_bin = key_stream(len(msg_bin))
        pad_bin = my_key_stream(len(msg_bin), random.randint(1, 999))
        print(bytes(pad_bin, "ascii"))
        enc = encrypt(bytes(msg_bin, 'ascii'),  bytes(pad_bin, 'ascii'))
        print('the encryption is: ')
        print(enc)
        print('back to decrypt in bytes: ')
        dec = decrypt(enc, bytes(pad_bin, 'ascii'))
        print(dec)
        print('back to decrypt in ascii: ')
        print(byte_to_text(dec))


#main()
