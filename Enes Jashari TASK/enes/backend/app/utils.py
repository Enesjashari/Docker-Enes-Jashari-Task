import math
from typing import List, Tuple


def is_prime(n: int) -> bool:

    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def count_primes_in_range(start: int, end: int) -> int:

    count = 0
    for num in range(start, end + 1):
        if is_prime(num):
            count += 1
    return count


def split_into_chunks(n: int, num_chunks: int) -> List[Tuple[int, int]]:

    chunk_size = n // num_chunks
    chunks = []
    
    for i in range(num_chunks):
        start = i * chunk_size + 1
        end = n if i == num_chunks - 1 else (i + 1) * chunk_size
        chunks.append((start, end))
    
    return chunks

