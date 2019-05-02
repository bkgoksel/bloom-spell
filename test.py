from bloom import BloomFilterSet

bloom_set = BloomFilterSet()

assert len(bloom_set._storage) * 8 == BloomFilterSet.INITIAL_SIZE
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
