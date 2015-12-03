
# Siggie - A Simple Tool for Graph Embedding

## Overview

Siggie is a simple tool for mapping a set of graphs to a set of
vectors. This mapping is referred to as graph embedding and allows for
applying techniques of machine learning and data mining to graphs.

Siggie implements a classic bag-of-words model for graphs. That is, a
graph is characterized by the occurences of subgraphs, where each
subgraph corresponds to one dimension of the vector space. Siggie
supports subgraphs of different complexity, which range from nodes and
edges to paths, componenents and closures.

## Limitations

Siggie does not support extracting arbitrary subgraphs, enumerating
graphlets as well as solving the subgraph isomorphism problem. Sorry,
it is a simple tool for a simple task.

Have fun, Konrad
