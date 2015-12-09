
# Siggie

Feature Hashing for Labeled Graphs.

## Overview

Siggie is a simple tool for mapping a set of labeled graphs to
vectors. The tool implements the classic bag-of-words model using
hashes of subgraphs.  That is, a labeled graph is characterized by the
hashes of selected subgraphs, where each hash corresponds to one
dimension of the vector space.  Siggie supports subgraphs of different
complexity, which range from the set of nodes and edges to connected
componenents, cliques and closures.

## Supported Modes

Siggie supports the following modes (types of subgraphs) for
feature hashing. A detailed description of each mode is given
in the next paragraphs.

        0: Bag of Nodes
        1: Bag of Edges
        2: Bag of Neighborhoods
        3: Nag of Reachabilities
        4: Bag of Shortest Paths
        5: Bag of Connected Components
        6: Bag of Attracting Components
        7: Bag of Elementary Cycles

For presenting the different modes, we first introduce a simple
toy example: The following graph consists of 6 nodes and 6 edges.
The nodes are labeled using the 3 symbols: `A`, `B` and `C`.

        A --> B <-- B --> C
              |     ^
              v     |
              C --> A

### Mode 0: Bag of Nodes

The graph is represented by a bag of the nodes. Note that only the
node labels are considered for constructing the bag and thus nodes
with the same label are mapped to the same entry, e.g. `A`.

        A:  2
        B:  2
        C:  2

### Mode 1: Bag of Edges

The graph is represented by a bag of the edges. Note again that only
the node labels are considered and different edges are mapped to the
same entry if their label pair matches, e.g. `A --> B`.

        A --> B:  2
        B --> B:  1
        B --> C:  2
        C --> A:  1

### Mode 2: Bag of Neighborhoods

The graph is represented by a bag of neighborhoods, that is, all nodes
reachable within a given neighborhood size of `N`. The following
example shows all neighborhoods of size 2. The nodes in each
neighborhood are sorted by labels and provided as a list. For example,
the neighborhood of size 2 for the left node `A` in the example graph
is `[B, C]`.

        A --> [B, B, C]:  1
        A --> [B, C]:     1
        B --> [A, C]:     1
        B --> [B, C, C]:  1
        C: []             1
        C --> [A, B]:     1

### Mode 3: Bag of Reachabilities

The graph is a represented by a bag of reachabilities, that is, all
pairs of nodes reachable within a given depth `N`. The following
example shows all reachabilities of depth 2 for the example graph.

        A --> B:  3
        A --> C:  2
        B --> A:  1
        B --> B:  1
        B --> C:  3
        C --> A:  1
        C --> B:  1

### Mode 4: Bag of Shortest Paths

The graph is represented by a bag of shortest paths. The length of the
paths can be bounded by a minimum `N` and a maximum `M`. Following are
all shortest paths with minimum length 2 and a maximum length 3.

        A --> B --> B:        1
        A --> B --> B --> C:  1
        A --> B --> C:        2
        A --> B --> C --> A:  1
        B --> B --> C:        1
        B --> B --> C --> A:  1
        B --> C --> A:        1
        B --> C --> A --> B:  1
        C --> A --> B:        1
        C --> A --> B --> B:  1
        C --> A --> B --> C:  1

### Mode 5: Bag of Connected Components

The graph is represented by a bag of strongly connected components. A
strongly connected component is a maximal subgraph in which each node
can reach all other nodes. The components are provided as lists, where
the nodes are sorted by label.

        [A]:           1
        [A, B, B, C]:  1
        [C]:           1

### Mode 6: Bag of Attracting Components

The graph is represented by a bag of attracting components. A
component is called attracting, if a random walker entering the
component would never leave it, thus being attracted.  The components
are provided as lists with nodes being sorted by label.

        [C]:  1

### Mode 7: Bag of Elementary Cycles

The graph is represented by a bag of elementary cycles, that is,
cycles that do not contain a node twice. The extracted cycles are
rotated, such that the smallest label is in front.

       A --> B --> B --> C:  1

### Limitations

Siggie does not support extracting arbitrary subgraphs. This also implies
that the tool cannot help in solving subgraph isomorphism problems. Please
relax, it is a simple tool for a simple task.

## Running Siggie

First of all, let us check that everything is working correctly.

      $ python sg_check.py
      .......
      Ran 7 tests in 0.027s
      OK

Analysing graphs can be computationally expensive. We thus benchmark
the different modes supported by Siggie. As an example dataset we use
`example.zip`, which contains 8 simple graphs in DOT format.

      $ python sg_bench.py example.zip
      = Loading graphs from bundle example.zip
      = Benchmarking modes for 1 seconds
      Mode: 0 |  1720 graphs/s |  0.58 ms/graph | +/-  0.46
      Mode: 1 |   544 graphs/s |  1.84 ms/graph | +/-  2.37
      Mode: 2 |   272 graphs/s |  3.68 ms/graph | +/-  4.96
      Mode: 3 |   202 graphs/s |  4.95 ms/graph | +/-  7.33
      Mode: 4 |   282 graphs/s |  3.54 ms/graph | +/-  5.66
      Mode: 5 |   663 graphs/s |  1.51 ms/graph | +/-  1.58
      Mode: 6 |   317 graphs/s |  3.15 ms/graph | +/-  3.96
      Mode: 7 |   151 graphs/s |  6.63 ms/graph | +/-  8.57

Looks good. We are now ready to map the graphs in `example.zip` to
vectors. To this end, we simply run the following command and pick
mode `4` which corresponds bags of shortest paths:

      $ python sg_map.py -m 4 -o vectors.libsvm example.zip
      = Loading graphs from bundle example.zip
      = Extracting bags of shortest paths (min: 3, max: 3) from graphs
      = Hashing bags to feature vectors
      = Saving feature vectors to vectors.libsvm


## Input Data

Siggie operates on so-called _bundles_ of graphs.  A bundle is a Zip archive
containing graphs as files in a format supported by Siggie.  You can provide
multiple bunldes to Siggie.  This comes handy if you have different classes
or types of graphs to analyze.

_File suffix:_ Every file entry in the archive with a `dot` suffix is
considered a graph in DOT format.  All other files are ignored.

_File label:_ Siggie can optionally extract a file label from the name of a
file entry using a regular expression.  By default, this regular expression
matches numbers at the beginning of file names.  For example, the file entry
`042_graph.dot` has the label `42`.  Note that leading zeros are dropped.

_Node labels:_ Siggie operates on labeled graphs.  Hence, the nodes of each
graph should be labeled using an attribute `label`. Depending on the 
particular format, this attribute needs to be added to each node.
