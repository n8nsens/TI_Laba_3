import math
import random


def fast_pow(base: int, exp: int, mod: int) -> int:
    res = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            res = (res * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return res

def egcd(a: int, b: int) -> tuple[int, int, int]:
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b:
        q, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0

def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError(f"gcd({a}, {m}) != 1. Обратный элемент не существует.")
    return x % m

def is_prime(n: int) -> bool:
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def prime_factors(n: int) -> list[int]:
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def find_primitive_roots(p: int) -> list[int]:
    if not is_prime(p): return []
    phi = p - 1
    factors = prime_factors(phi)
    roots = []
    for g in range(2, p):
        if all(fast_pow(g, phi // q, p) != 1 for q in factors):
            roots.append(g)
    return roots

BLOCK_SIZE = 2  

def elgamal_encrypt(data: bytes, p: int, g: int, x: int, initial_k: int) -> tuple[list[tuple[int, int]], int]:
    if not is_prime(p):
        raise ValueError("Модуль p должен быть простым числом.")
    if p <= (2 ** (BLOCK_SIZE * 8) - 1):
        raise ValueError(f"Для блоков {BLOCK_SIZE} байта модуль p должен быть > {(2**(BLOCK_SIZE*8)-1)}")
    if not (1 < x < p - 1):
        raise ValueError("Закрытый ключ x должен удовлетворять: 1 < x < p-1")
    if not (1 < initial_k < p - 1) or math.gcd(initial_k, p - 1) != 1:
        raise ValueError("Начальный k должен быть: 1 < k < p-1 и gcd(k, p-1) == 1")

    roots = find_primitive_roots(p)
    if g not in roots:
        raise ValueError("g не является первообразным корнем по модулю p")

    padding_len = (BLOCK_SIZE - len(data) % BLOCK_SIZE) % BLOCK_SIZE
    padded = data + b'\x00' * padding_len

    y = fast_pow(g, x, p)
    blocks = []

    random.seed(initial_k)
    k = initial_k 

    for i in range(0, len(padded), BLOCK_SIZE):
        m = int.from_bytes(padded[i:i+BLOCK_SIZE], 'big')
        if m >= p:
            raise RuntimeError(f"Блок {m} >= p. Увеличьте p.")

        if i > 0:
            while True:
                k = random.randint(2, p - 2)
                if math.gcd(k, p - 1) == 1:
                    break

        a = fast_pow(g, k, p)
        b = (m * fast_pow(y, k, p)) % p
        blocks.append((a, b))

    return blocks, padding_len

def elgamal_decrypt(blocks: list[tuple[int, int]], p: int, x: int, padding_len: int) -> tuple[bytes, list[int]]:
    if not is_prime(p):
        raise ValueError("Модуль p должен быть простым числом.")
    if not (1 < x < p - 1):
        raise ValueError("Неверный закрытый ключ x")

    decrypted_vals = []
    byte_stream = b''

    for a, b in blocks:
        ax = fast_pow(a, x, p)
        inv_ax = modinv(ax, p)
        m = (b * inv_ax) % p
        decrypted_vals.append(m)
        byte_stream += m.to_bytes(BLOCK_SIZE, 'big')

    if padding_len > 0:
        byte_stream = byte_stream[:-padding_len]
        
    return byte_stream, decrypted_vals