"""
A Python 3.7 implementation of a Set based on a Bloom Filter
"""
from typing import TypeVar, Container, Tuple, Optional
import math
import sys


T = TypeVar("T")


class BloomFilterSet(Container[T]):
    """
    The BloomFilter Set class
    """

    _storage: bytearray  # Actual byte storage for the filter
    _bit_width: int  # Size of storage in bits
    _num_adds: int  # Number of times elements were added
    _num_hashes: int  # Number of hash functions used
    _word_size: int  # Word size of the underlying interpreter (used for double hashing)
    _right_mask: int  # Mask for the right half of an expected hash value (used for double hashing)
    _left_mask: int  # Mask for the left half of an expected hash value (used for double hashing)

    MIN_NUM_HASHES: int = 3  # Minimum number of hash functions to use when calculating optimal
    MAX_NUM_HASHES: int = 32  # Maximum number of hash functions to use when calculating optimal
    DEFAULT_BYTE_SIZE: int = 1024 * 1024  # Default size (in bytes) to use for filter if not specified

    def __init__(
        self,
        byte_size: int = DEFAULT_BYTE_SIZE,
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
        self._num_adds = 0
        # Only support 64 and 32bit, sys.maxsize returns largest expected hash value
        self._word_size: int = 64 if sys.maxsize > 2 ** 32 else 32
        # Set all the bits on the right half of word size bits to 1
        self._right_mask = (2 ** (self._word_size // 2)) - 1
        # Do the same but shift left. Notice the -1 to account for the sign bit
        self._left_mask = ((2 ** ((self._word_size // 2) - 1)) - 1) << (
            self._word_size // 2
        )
        self._storage = bytearray(self._bit_width // 8)
        if expected_number_of_entries is not None:
            # Formula for optimal number floor(ln(2)*m/n) from Wikipedia
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

    def _set_bit(self, idx: int) -> None:
        """
        Taking a bit index idx (offset from right), find the corresponding byte
        and the corresponding bit in it in our storage and set that bit to 1
        """
        byte_idx_to_modify = idx // 8
        bit_idx_to_modify = idx % 8
        self._storage[byte_idx_to_modify] |= 1 << bit_idx_to_modify

    def _check_bit(self, idx: int) -> bool:
        """
        Taking a bit index idx (offset from right), find the corresponding byte
        and the corresponding bit in it in our storage and check that the bit is 1
        """
        byte_idx_to_modify = idx // 8
        bit_idx_to_modify = idx % 8
        return bool(self._storage[byte_idx_to_modify] & (1 << bit_idx_to_modify))

    def _hash(self, element: T) -> Tuple[int]:
        """
        Given an element, compute all the bits that it hashes to in our bit vector
        """
        full_hash = hash(element)
        #  Mask out the rightmost half of the bits of the hash value
        left_hash = (full_hash & self._left_mask) >> (self._word_size // 2)
        #  Mask out the leftmost half of the bits of the hash value
        right_hash = full_hash & self._right_mask
        #  Refer to Wikipedia for formula for double hashing:
        hashes = (
            (left_hash + hash_idx * right_hash) % self._bit_width
            for hash_idx in range(self._num_hashes)
        )
        return tuple(hashes)

    def add(self, element: T) -> None:
        """
        Adds an element to the set
        Also incrementes element count by one.
        :param element: Element to be added
        """
        hashes = self._hash(element)
        for hash_idx in hashes:
            self._set_bit(hash_idx)
        self._num_adds += 1

    def __contains__(self, element: T) -> bool:
        """
        Checks whether an element is in the set.
        May return false positives (ie True for elements not in set)
        Never returns false negatives
        :param element: Element to check for membership
        :returns: Bool that if True indicates element may be in the set,
                if False, the element was definitely never added to the set
        """
        hashes = self._hash(element)
        #  If all the hashed bits of an element are set, assume it was added
        return all(self._check_bit(hash_idx) for hash_idx in hashes)

    @property
    def size(self) -> int:
        """
        Since Bloom Filers are approximate sized, each `add` call
        increments size by 1, as a result this returns number of times
        `add` was called on the set
        :returns: Int, number of times any element was added to the set
        """
        #  Note: a better approximation of the true size is known, but
        #  plain number of additions were picked for transparency.
        #  refer to Wikpedia for the formula for the better true approximation
        return self._num_adds

    @property
    def false_positive_prob(self) -> float:
        """
        Get the current false positive probability (upper bound)
        Calculates the probability assuming each added element was unique
        :returns: Float, probability that the membership check returns a false positive
        """
        #  Refer to Wikipedia for the formula for the false positive probability calculation
        return (
            1 - math.e ** ((-1 * self._num_hashes * self._num_adds) / self._bit_width)
        ) ** self._num_hashes
