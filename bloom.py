"""
A Python 3.7 implementation of a Set based on a Bloom Filter
"""
from typing import TypeVar, Container, Tuple, Any, Optional
import hashlib
import math
import sys


T = TypeVar("T")


class BloomFilterSet(Container[T]):
    """
    The BloomFilter Set class
    """

    _storage: bytearray
    _bit_width: int
    _num_elems: int
    _num_hashes: int
    _word_size: int
    _right_mask: int
    _left_mask: int

    HASH_FUNCTION: Any = hashlib.md5
    MIN_NUM_HASHES: int = 3
    MAX_NUM_HASHES: int = 32
    INITIAL_SIZE: int = 1024 * 1024

    def __init__(
        self,
        byte_size: int = INITIAL_SIZE,
        expected_number_of_entries: Optional[int] = None,
        num_hashes: Optional[int] = None,
    ) -> None:
        """
        Creates a new BloomFilterSet. You can either specify the number of
        hash functions to be used directly or specify the expected number
        of entries to be put into the bloom filter and have it pick the
        optimal number of hash functions based on the size and expected
        load.
        :param byte_size: Size of the Bloom filter storage in bytes
        :param expected_number_of_entries: Expected number of entries to be added, optional
        :param num_hashes: Number of hashes to use for adding elements. Optional, should not be set if expected_number_of_entries is set
        """
        if expected_number_of_entries is None and num_hashes is None:
            raise ValueError(
                "You must specify either num_hashes or expected_number_of_entries to initialize the Bloom Filter Set"
            )
        if expected_number_of_entries is not None and num_hashes is not None:
            raise ValueError(
                "You must specify only one of num_hashes or expected_number_of_entries to initialize the Bloom Filter Set"
            )

        self._bit_width = byte_size * 8
        self._num_elems = 0
        self._word_size: int = 64 if sys.maxsize > 2 ** 32 else 32
        self._right_mask = (2 ** (self._word_size // 2)) - 1
        self._left_mask = ((2 ** ((self._word_size // 2) - 1)) - 1) << (
            self._word_size // 2
        )
        self._initialize_storage()
        if expected_number_of_entries is not None:
            self._num_hashes = max(
                min(
                    math.floor(
                        math.log(2) * self._bit_width / expected_number_of_entries
                    ),
                    self.MAX_NUM_HASHES,
                ),
                self.MIN_NUM_HASHES,
            )
        else:
            self._num_hashes = num_hashes

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

    def _hash(self, element: T) -> Tuple[int]:
        full_hash = hash(element)
        left_hash = (full_hash & self._left_mask) >> (self._word_size // 2)
        right_hash = full_hash & self._right_mask
        hashes = (
            (left_hash + hash_idx * right_hash) % self._bit_width
            for hash_idx in range(self._num_hashes)
        )
        return tuple(hashes)

    def add(self, element: T) -> None:
        """
        Adds an element to the set
        Also incrementes element count by one.
        """
        hashes = self._hash(element)
        for hash_idx in hashes:
            self._hash_bit(hash_idx)
        self._num_elems += 1

    def __contains__(self, element: T) -> bool:
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
