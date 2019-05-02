# Bloom-filter based Spell Checker

This is a very simple spell checker that uses a bloom filter to store arbitrarily large
vocabularies.

The spell checking tokenizes sentences on whitespace and marks each token as either in or outside is vocabulary.

Since the storage is a Bloom filter, it might mistakenly mark out-of-vocabulary words as in-vocabulary words, thus misisng
actual misspellings.

To use it import `SpellChecker` from `spell`. It expects a line-delimited file of all the words in your vocabulary.

Use the spell checker with `checker.spell_check('Example sentence here')`.

To run tests, invoke `nosetests`.


Built as a code sample.
