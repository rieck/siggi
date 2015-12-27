# Open Issues

- Normalization of feature vectors: l1, l2, None
- Support for binary and frequency maps
- Signed feature hashing by Weinberger et al.
- Bag of connected graphlets by Shervashidze et al.
- Simplification/sanitization of parameters
- Implementation of generalized Floyd-Warshal algorithm

# Interesting Issues

## Semirings

We define a simplified semiring by a `set`, `plus`, `zero`, `prod`, `one`,
where `zero` is the neutral elment of `plus`, `one` the neutral elment of
`prod` and `set` the set we are operating with.

### Shortest Paths

The classic all-pairs shortest-path problem can be solved using
this semiring.

- `set`: positive integers
- `plus`: addition
- `zero`: 0
- `prod`: minimum operation
- `one`: infinity

### Transitive Closure

The transitive closure of a graph, that is, the all-pairs reachability,
can be solved using the following semiring. However, due to the binary
set there exist more efficient implementations.

- `set`: 0,1
- `plus`: and operation
- `zero`: 1
- `prod`: or operation
- `one`: 0

### Bottleneck Paths

The all-pairs bottlneck-path problem can be solved using this semiring.

- `set`: positive integers
- `plus`: minimum operation
- `zero`: infinity
- `prod`: maximum operation
- `one`: 0
