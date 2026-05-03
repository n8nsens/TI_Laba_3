import math
import random

def fast_pow(base: int, exp: int, mod: int) -> int:
    res = 1
    base %= mod
    while exp > 0:
        if exp & 1: res = (res * base) % mod
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
    if g != 1: raise ValueError("Обратного элемента нет")
    return x % m

def is_prime(n: int) -> bool:
    if n < 2: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    return True

def find_primitive_roots(p: int) -> list[int]:
    if not is_prime(p): return []
    phi = p - 1
    factors = []
    d, n = 2, phi
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0: n //= d
        d += 1
    if n > 1: factors.append(n)
    
    roots = []
    for g in range(2, p):
        if all(fast_pow(g, phi // q, p) != 1 for q in factors):
            roots.append(g)
    return roots

def elgamal_encrypt(data: bytes, p: int, g: int, x: int, initial_k: int) -> tuple[list[tuple[int, int]], int]:
    y = fast_pow(g, x, p)
    blocks = []
    random.seed(initial_k)
    k = initial_k
    for m in data:
        a = fast_pow(g, k, p)
        b = (m * fast_pow(y, k, p)) % p
        blocks.append((a, b))
        while True:
            k = random.randint(2, p - 2)
            if math.gcd(k, p - 1) == 1: break
    return blocks, 0

def elgamal_decrypt(blocks: list[tuple[int, int]], p: int, x: int, padding_len: int) -> tuple[bytes, list[int]]:
    byte_stream = bytearray()
    for a, b in blocks:
        m = (b * modinv(fast_pow(a, x, p), p)) % p
        byte_stream.append(m)
    return bytes(byte_stream), []