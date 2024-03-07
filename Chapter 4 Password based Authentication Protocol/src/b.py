import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# 生成AES密钥
def generate_aes_key():
    return get_random_bytes(16)  # 128位密钥

# AES加密
def aes_encrypt(key, data):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    return cipher.iv + ciphertext

# AES解密
def aes_decrypt(key, data):
    iv = data[:AES.block_size]
    ciphertext = data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext

# RSA加密
def rsa_encrypt(public_key, data):
    cipher_rsa = PKCS1_OAEP.new(public_key)
    ciphertext = cipher_rsa.encrypt(data)
    return ciphertext

# RSA解密
def rsa_decrypt(private_key, data):
    cipher_rsa = PKCS1_OAEP.new(private_key)
    plaintext = cipher_rsa.decrypt(data)
    return plaintext

def main():
    # 创建TCP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345)
    print("Connecting to server...")
    sock.connect(server_address)
    print("Connected to server.")

    try:
        # 第一步：接收A发送的加密的公钥pkA
        encrypted_public_key = sock.recv(2048)
        public_key = aes_decrypt(pw, encrypted_public_key)
        print("解密得到pkA:")
        print(public_key)

        # 第二步：B生成会话密钥Ks，并将Ks用A的公钥pkA加密后发送给A
        ks = generate_aes_key()
        print("随机生成Ks:")
        print(ks)
        encrypted_ks = aes_encrypt(pw, rsa_encrypt(RSA.import_key(public_key), ks))
        sock.sendall(encrypted_ks)

        # 第三步：接收A发送的加密的NA，并用Ks解密
        encrypted_na = sock.recv(2048)
        na = aes_decrypt(ks, encrypted_na)
        print("解密得到NA:")
        print(na)

        # 第四步：B生成NB，并将NA、NB用Ks加密后发送给A
        nb = get_random_bytes(16)
        print("随机生成NB:")
        print(nb)
        encrypted_na_nb = aes_encrypt(ks, na + nb)
        sock.sendall(encrypted_na_nb)

        # 第五步：接收A发送的加密的NB，并验证NB是否正确
        encrypted_nb = sock.recv(2048)
        decrypted_nb = aes_decrypt(ks, encrypted_nb)
        print("验证NB:")
        if decrypted_nb == nb:
            print("验证成功，认证结束，采用Ks作为共享的对称密钥通信")
            print("Ks:")
            print(ks)
            encrypted_message = sock.recv(2048)
            message = aes_decrypt(ks, encrypted_message)
            print("message:")
            print(message)

        else:
            print("验证失败，请重试...")

    finally:
        sock.close()

if __name__ == '__main__':
    # 共享的秘密口令
    pw = b'mysecretpassword'
    main()
