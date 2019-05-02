from bloom import BloomFilterSet
from spell import SpellChecker

bloom_set = BloomFilterSet(expected_number_of_entries=2)

assert len(bloom_set._storage) == BloomFilterSet.INITIAL_SIZE
assert bloom_set.approximate_size == 0

assert(bloom_set._hash('0') == bloom_set._hash('0'))

bloom_set.add('0')
assert '0' in bloom_set
assert bloom_set.approximate_size == 1
bloom_set.add('asdf')
assert 'asdf' in bloom_set
assert '0' in bloom_set
assert bloom_set.approximate_size == 2
print(bloom_set.approximate_false_positive_prob)

spell = SpellChecker('test-vocab.txt')

assert 'hello' in spell
assert 'world' in spell

result = spell.spell_check('hello world wrold')
assert result == [False, False, True], result

print(spell.vocab._num_hashes)
print(spell.vocab.approximate_false_positive_prob)


spell = SpellChecker('all_of_english.txt')

assert 'hello' in spell
assert 'world' in spell

result = spell.spell_check('hello world wrold')
assert result == [False, False, True], result
print(spell.vocab._num_hashes)
