"""
Implementation of a spellchecker that uses a Bloom filter to store its vocabulary
"""
from typing import List
from bloom import BloomFilterSet


class SpellChecker:
    """
    A simple SpellChecker that stores vocabularies of arbitrary size using
    a Bloom filter to catch out-of-dictionary words
    """

    vocab: BloomFilterSet
    vocab_size: int

    def __init__(self, vocab_file_path: str, filter_size_bytes: int = None) -> None:
        """
        Creates a new SpellChecker, reading vocabulary from a given file
        For fun let's assume the vocabulary doesn't fit in our memory
        :param vocab_file_path: Path to vocab file, should include one word per line
        :param filter_size_bytes: Size of underlying filter in bytes, default value of 1MB used if not specified
        """
        self.vocab_size = 0
        with open(vocab_file_path, "r") as vocab_file:
            # First approximate the number of words by dividing the file size by the average word length
            # This is to avoid reading the entire file just to get the number of words
            # We need the number of words first to properly optimize our Bloom filter before adding
            # words to it.
            vocab_file.seek(0, 2)
            file_size = vocab_file.tell()
            num_words = (
                file_size / 8
            )  # Average English word is 8 characters long
            vocab_file.seek(0)
            if filter_size_bytes:
                self.vocab = BloomFilterSet(
                    expected_number_of_entries=num_words,
                    byte_size=filter_size_bytes,
                )
            else:
                self.vocab = BloomFilterSet(
                    expected_number_of_entries=num_words
                )
            for word in vocab_file:
                self.vocab.add(word.strip())
                self.vocab_size += 1

    def __contains__(self, word: str) -> bool:
        return word in self.vocab

    def __len__(self) -> int:
        return self.vocab_size

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

    @property
    def false_positive_prob(self) -> float:
        """
        Returns the approximate probability that any given misspelled word
        will not be caught by the spellchecker. The uncertainty is due to
        the underlying Bloom filter used to store the vocabulary
        """
        return self.vocab.false_positive_prob
