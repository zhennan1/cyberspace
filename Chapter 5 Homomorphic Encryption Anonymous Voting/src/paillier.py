import random
import math


def generate_key_pair():
    # 生成密钥对
    p = generate_large_prime()
    q = generate_large_prime()
    N = p * q
    lambda_val = lcm(p - 1, q - 1)

    g = random.randint(1, N**2)  # 随机选择g
    while math.gcd(L(g, N), N) != 1:
        g = random.randint(1, N**2)

    public_key = (N, g)
    private_key = lambda_val

    return public_key, private_key


def encrypt(public_key, m):
    N, g = public_key
    r = random.randint(1, N)
    ciphertext = (pow(g, m, N**2) * pow(r, N, N**2)) % (N**2)
    return ciphertext


def decrypt(private_key, public_key, ciphertext):
    N, g = public_key
    lambda_val = private_key
    numerator = L(pow(ciphertext, lambda_val, N**2), N)
    denominator = L(pow(g, lambda_val, N**2), N)
    plaintext = (numerator * inverse(denominator, N)) % N
    return plaintext


def generate_large_prime():
    # 生成大素数
    while True:
        num = random.randint(2**15, 2**16)  # 生成15位随机数
        if is_prime(num):
            return num


def is_prime(n):
    # 判断是否为素数
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def lcm(a, b):
    # 计算最小公倍数
    return abs(a * b) // math.gcd(a, b)


def L(x, N):
    # L函数
    return (x - 1) // N


def inverse(a, N):
    # 计算a模N的逆元
    g, x, _ = extended_gcd(a, N)
    if g == 1:
        return x % N
    return None


def extended_gcd(a, b):
    # 扩展欧几里得算法
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def main():
    public_key, private_key = generate_key_pair()  # 密钥生成

    n = int(input("请输入候选者人数："))
    m = int(input("请输入投票者人数："))

    # 创建一个m行n列的二维数组
    array = []
    for i in range(m):
        row = []
        print("请输入第", i + 1, "张选票，'1'表示选，'0'表示不选，用空格隔开：")
        values = input().split()  # 将输入字符串拆分为多个部分
        row = list(map(int, values))  # 将每个部分转换为整数
        array.append(row)

    cipher = []
    plain = []
    for i in range(n):
        cipher.append(1)
        plain.append(1)

    for i in range(n):
        for j in range(m):
            array[j][i] = encrypt(public_key, array[j][i])

    print("每张选票对应的密文：")
    for i in range(m):
        print(array[i])

    for i in range(n):
        for j in range(m):
            cipher[i] = cipher[i] * array[j][i]
            plain[i] = decrypt(private_key, public_key, cipher[i])

    print("各候选人得票情况对应的密文：")
    for i in range(n):
        print(cipher[i])

    print("各候选人得票情况如下：")
    for i in range(n):
        print("候选人", i + 1, "：", end="")
        print(plain[i])

    max_value = max(plain)
    max_indices = [i + 1 for i, value in enumerate(plain) if value == max_value]
    print("得票最高的候选人是：", max_indices)

    
if __name__ == '__main__':
    main()
