
# Siggie

Feature Hashing for Labeled Graphs.

## Overview

Siggie is a simple tool for mapping a set of labeled graphs to vectors. The
tool implements the classic bag-of-words model using hashes of subgraphs.
That is, a labeled graph is characterized by the hashes of selected
subgraphs, where each hash corresponds to one dimension of the vector space.
Siggie supports subgraphs of different complexity, which range from the set
of nodes and edges to connected componenents, cliques and closures.

## Limitations

Siggie does not support extracting arbitrary subgraphs, as well as solving
the subgraph isomorphism problem. It is a simple tool for a simple task.

## Supported Bags of Subgraphs

For presenting the different types of subgraphs, we first introduce  a simple
toy example: The following graph consists of 6 nodes and 6 edges. The nodes
are labeled using the 3 symbols: `A`, `B` and `C`.

        A --> B <-- B --> C
              |     ^
              v     |
              C --> A

### Bag of Nodes

The graph is represented by a bag of the nodes.

        A: 2
        B: 2
        C: 2

### Bag of Edges

The graph is represented by a bag of the edges.

        A --> B: 2
        B --> B: 1
        B --> C: 2
        C --> A: 1

### Bag of Neighborhoods

The graph is represented by a bag of neighborhoods, that is, all nodes
reachable within a given neighborhood size of `N`. The following example
shows all neighborhoods of size 2. Note that the nodes are sorted by labels.

        A --> B, C: 1
        A --> B, B, C: 1
        B --> A, C: 1
        B --> B, C, C: 1
        C --> A, B: 1
        C: 1

### Bag of Reachabilities

The graph is a represented by a bag of reachabilities, that is, all pairs of
nodes reachable within a given depth `N`. The following example shows all
reachabilities of depth 2 for the example graph.

        A --> B: 2
        A --> C: 2
        B --> A: 1
        B --> B: 1
        B --> C: 3
        C --> A: 1
        C --> B: 1

### Bag of Shortest Paths

The graph is represented by a bag of shortest paths. The length of the paths
can be bounded by a minimum `N` and a maximum `M`. Following are all shortest
paths with a minimum length of 2 and a maximum length of 3.

        A --> B --> C: 2
        A --> B --> B: 1
        A --> B --> B --> C: 1        
        A --> B --> C --> A: 1
        B --> B --> C: 1
        B --> B --> C --> A: 1
        B --> C --> A: 1
        B --> C --> A --> B: 1
        C --> A --> B: 1
        C --> A --> B --> B: 1
        C --> A --> B --> C: 1
