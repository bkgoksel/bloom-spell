"""
Test module for the Bloom Filter and the Bloom filter backed spell checker
Run nosetests to dispatch the tests
"""
import random
import sys
import math

from bloom import BloomFilterSet
from spell import SpellChecker


def test_filter_instantiation():
    # Make sure filter is instantiated properly
    bloom_set = BloomFilterSet(num_hashes=12)
    assert len(bloom_set._storage) == BloomFilterSet.DEFAULT_BYTE_SIZE
    assert bloom_set.size == 0


def test_filter_hash():
    # Make sure hashing passes all sanity checks
    bloom_set = BloomFilterSet(num_hashes=12)
    assert bloom_set._hash("0") == bloom_set._hash("0")
    assert bloom_set._hash(123) == bloom_set._hash(123)
    assert bloom_set._hash(("asdflljl", 123)) == bloom_set._hash(("asdflljl", 123))


def test_filter_add():
    # Make sure added elements are easily found
    bloom_set = BloomFilterSet(expected_number_of_entries=1)
    bloom_set.add("0")
    assert "0" in bloom_set
    assert bloom_set.size == 1


def test_filter_multi_add():
    # Make sure adding multiple elements works
    bloom_set = BloomFilterSet(expected_number_of_entries=2)
    bloom_set.add("0")
    bloom_set.add("asdf")
    assert "0" in bloom_set
    assert "asdf" in bloom_set
    assert bloom_set.size == 2


def test_filter_false_prob():
    # Make sure the filter is right about its false positive rate
    bloom_set = BloomFilterSet(byte_size=16, num_hashes=3)
    bloom_set.add('0')
    bloom_set.add('5')
    bloom_set.add('10')
    bloom_set.add('12')
    false_positives = 0
    num_tries = 100000
    for _ in range(num_tries):
        if random.randint(0, sys.maxsize) in bloom_set:
            false_positives += 1
    fpr = false_positives / num_tries
    assert math.fabs(fpr - bloom_set.false_positive_prob) < 1e-3


def test_spell_check_full_test_vocab():
    # Make sure the spell check includes all its vocab
    spell = SpellChecker("test-vocab.txt")
    assert "hello" in spell
    assert "world" in spell


def test_spell_check_sentence_check():
    # Make sure the spell check works on a sentence
    spell = SpellChecker("test-vocab.txt")
    result = spell.spell_check("hello world wrold")
    assert result == [False, False, True]


def test_spell_check_all_of_english():
    # Make sure the spell check can handle the entire english vocab
    spell = SpellChecker("all_of_english.txt")
    assert "hello" in spell
    assert "world" in spell
    result = spell.spell_check("hello world wrold")
    assert result == [False, False, True], result


def test_spell_check_false_prob():
    # Make sure the spell check is roughly correct about its FPR
    spell = SpellChecker("all_of_english.txt", filter_size_bytes=64 * 1024)
    num_tries = 10000
    false_positives = 0
    for _ in range(num_tries):
        if random.randint(0, sys.maxsize) in spell:
            false_positives += 1
    fpr = false_positives / num_tries
    assert math.fabs(fpr - spell.false_positive_prob) < 1e-2
