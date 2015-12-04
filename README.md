
# Siggie

Feature Hashing for Labeled Graphs.

## Overview

Siggie is a simple tool for mapping a set of labeled graphs to vectors.
The tool implements the classic bag-of-words model using hashes of
subgraphs. That is, a labeled graph is characterized by the hashes of
selected subgraphs, where each hash corresponds to one dimension of the
vector space. Siggie supports subgraphs of different complexity, which
range from the set of nodes and edges to connected componenents, cliques
and closures.

## Limitations

Siggie does not support extracting arbitrary subgraphs, as well as
solving the subgraph isomorphism problem. It is a simple tool for a
simple task.

Have fun, Konrad
