"""
A Python 3.7 implementation of a Set based on a Bloom Filter
"""
from typing import Tuple, Any
import hashlib
import math
import sys


class BloomFilterSet:
    """
    The BloomFilter Set class
    """

    _storage: bytearray
    _bit_width: int
    _num_elems: int
    _num_hashes: int
    _hash_fn: Any
    _word_size: int

    HASH_FUNCTION: Any = hashlib.md5
    NUM_HASHES: int = 8
    INITIAL_SIZE: int = 2 ** 10

    def __init__(
        self,
        bit_width: int = INITIAL_SIZE,
        num_hashes: int = NUM_HASHES,
        hash_fn: Any = HASH_FUNCTION,
    ) -> None:
        self._bit_width = bit_width
        self._hash_fn = hash_fn
        self._num_hashes = num_hashes
        self._num_elems = 0
        self._word_size = 64 if sys.maxsize > 2**32 else 32
        self._initialize_storage()

    def _initialize_storage(self) -> None:
        self._storage = bytearray(self._bit_width // 8)

    def _hash_bit(self, idx: int) -> None:
        byte_idx_to_modify = idx // 8
        bit_idx_to_modify = idx % 8
        self._storage[byte_idx_to_modify] |= 1 << bit_idx_to_modify

    def _check_bit(self, idx: int) -> bool:
        byte_idx_to_modify = idx // 8
        bit_idx_to_modify = idx % 8
        return bool(self._storage[byte_idx_to_modify] & (1 << bit_idx_to_modify))

    def _hash(self, element: str) -> Tuple[int]:
        big_hash = self._hash_fn(element.encode())
        hash_half_len = big_hash.digest_size // 2
        hash_digest = big_hash.digest()
        first_hash, second_hash = (
            int.from_bytes(hash_digest[:hash_half_len], "little"),
            int.from_bytes(hash_digest[hash_half_len:], "little"),
        )
        hashes = (
            (first_hash + hash_idx * second_hash) % self._bit_width
            for hash_idx in range(self._num_hashes)
        )
        return tuple(hashes)

    def add(self, element: str) -> None:
        """
        Adds an element to the set
        Also incrementes element count by one.
        """
        hashes = self._hash(element)
        for hash_idx in hashes:
            self._hash_bit(hash_idx)
        self._num_elems += 1

    def __contains__(self, element: str) -> bool:
        """
        Checks whether an element is in the set.
        May return false positives (ie True for elements not in set)
        Never returns false negatives
        """
        hashes = self._hash(element)
        return all(self._check_bit(hash_idx) for hash_idx in hashes)

    @property
    def approximate_size(self) -> int:
        """
        Since Bloom Filers are approximate sized, each `add` call
        increments size by 1, as a result this returns number of times
        `add` was called on the set
        """
        return self._num_elems

    @property
    def approximate_false_positive_prob(self) -> float:
        """
        Returns the current expected false positive probability of the
        Bloom filter given its parameters.
        """
        return (
            1 - math.e ** ((-1 * self._num_hashes * self._num_elems) / self._bit_width)
        ) ** self._num_hashes
