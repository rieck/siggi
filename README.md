
Siggie - A Simple Tool for Graph Embedding
==

Overview
--

Siggie is a simple tool for mapping a set of graphs to a set of
vectors. This mapping is referred to as embedding and allows for
applying techniques of machine learning and data mining for analysis
of graphs. In particular, Siggie implements a classic bag-of-words
model for graphs, where a graph is mapped to a vector based on the
subgraphs it contains. These subgraphs can be simply nodes and edges
but also more involved constructs, such as paths, componenents and
closures.

Limitations
--

Siggie does not support extracting arbitrary subgraphs, enumerating
graphlets as well as solving the subgraph isomorphism problem. Sorry,
it is a simple tool.

Have fun, Konrad
