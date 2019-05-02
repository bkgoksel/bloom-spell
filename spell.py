"""
Implementation of a spellchecker that uses a Bloom filter to store its vocabulary
"""
from typing import List
from bloom import BloomFilterSet


class SpellChecker():
    """
    A simple SpellChecker that stores vocabularies of arbitrary size using
    a Bloom filter to catch out-of-dictionary words
    """
    def __init__(
            self,
            vocab_file_path: str,
            filter_size_bytes: int = None) -> None:
        """
        Creates a new SpellChecker, reading vocabulary from a given file
        For fun let's assume the vocabulary doesn't fit in our memory
        :param vocab_file_path: Path to vocab file, should include one word per line
        :param filter_size_bytes: Size of underlying filter in bytes, default value of 1MB used if not specified
        """
        vocab: BloomFilterSet

        with open(vocab_file_path, 'r') as vocab_file:
            vocab_file.seek(0, 2)
            file_size = vocab_file.tell()
            approximate_num_words = file_size / 8  # Average English word is 8 characters long
            vocab_file.seek(0)
            if filter_size_bytes:
                self.vocab = BloomFilterSet(expected_number_of_entries=approximate_num_words, byte_size=filter_size_bytes)
            else:
                self.vocab = BloomFilterSet(expected_number_of_entries=approximate_num_words)
            for word in vocab_file:
                self.vocab.add(word.strip())

    def __contains__(self, word: str) -> bool:
        return word in self.vocab

    def spell_check(self, text: str) -> List[bool]:
        """
        Spellchecks a given sentence, splits the given
        text on whitespace and lowercases it before checking whether each
        token is in the vocabulary.
        :param text: A String of space-delimited tokens
        :returns: A List of bools, same length as the sentence, True where
                    the token might be a misspelling
        """
        return [word.lower() not in self.vocab for word in text.split()]
