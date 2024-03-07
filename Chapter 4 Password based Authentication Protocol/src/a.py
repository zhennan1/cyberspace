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

# 生成RSA密钥对
def generate_rsa_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def main():
    # 创建TCP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345)
    sock.bind(server_address)
    sock.listen(1)
    print("Waiting for connection...")

    # 等待客户端连接
    connection, client_address = sock.accept()
    print("Connection established with", client_address)

    try:
        # 第一步：A随机生成RSA密钥对并发送给B
        private_key, public_key = generate_rsa_key_pair()
        print("生成密钥对(pkA,sKA)，pkA:")
        print(public_key)

        connection.sendall(aes_encrypt(pw, public_key))

        # 第二步：接收B发送的加密的会话密钥Ks
        encrypted_ks = connection.recv(2048)
        ks = rsa_decrypt(RSA.import_key(private_key), aes_decrypt(pw, encrypted_ks))
        print("解密得到Ks:")
        print(ks)

        # 第三步：A生成NA，并将NA用Ks加密后发送给B
        na = get_random_bytes(16)
        print("随机生成NA:")
        print(na)
        encrypted_na = aes_encrypt(ks, na)
        connection.sendall(encrypted_na)
        
        # 第四步：接收B发送的加密的NA和NB，并验证NA是否正确
        encrypted_na_nb = connection.recv(2048)
        decrypted_na_nb = aes_decrypt(ks, encrypted_na_nb)
        received_na = decrypted_na_nb[:16]
        received_nb = decrypted_na_nb[16:]
        print("解密得到NB:")
        print(received_nb)
        print("验证NA:")
        if received_na == na:
            # 第五步：验证通过，A用Ks加密NB发送给B
            encrypted_nb = aes_encrypt(ks, received_nb)
            connection.sendall(encrypted_nb)
            print("验证通过，用Ks加密NB发送给B，采用Ks作为共享的对称密钥通信")
            print("Ks:")
            print(ks)
            message = b'success!'
            print("message:")
            print(message)
            encrypted_message = aes_encrypt(ks, message)
            connection.sendall(encrypted_message)

        else:
            print("验证失败，请重试...")

    finally:
        connection.close()
        sock.close()

if __name__ == '__main__':
    # 共享的秘密口令
    pw = b'mysecretpassword'
    main()
