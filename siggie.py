# Siggie - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import sys
from collections import defaultdict

import networkx as nx

import utils


# Supported modes for bags
modes = {
    0: "bag_of_nodes",
    1: "bag_of_edges",
    2: "bag_of_neighbors",
    3: "bag_of_weakly_connected_components",
    4: "bag_of_strongly_connected_components",
    5: "bag_of_attracting_components",
    6: "bag_of_transitive_closure",
    7: "bag_of_shortest_paths",
}


def bag_of_nodes(graph):
    """ Build bag of nodes from graph """

    bag = {}
    for i in graph.nodes():
        label = graph.node[i]["label"]
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_edges(graph):
    """ Build bag of edges from graph """

    bag = {}
    for i, j in graph.edges():
        label = "%s-%s" % (graph.node[i]["label"], graph.node[j]["label"])
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_neighbors(graph):
    """ Build bag of neighbors from graph """

    bag = {}
    for i in graph.nodes():
        ns = map(lambda x: graph.node[x]["label"], graph.neighbors(i))
        label = "%s:%s" % (graph.node[i]["label"], '-'.join(sorted(ns)))
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_transitive_closure(graph, maxlen=None):
    """ Build bag of transitive closure for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=maxlen)

    bag = {}
    for i in paths:
        for j in paths[i]:
            if i == j:
                continue
            label = "%s:%s" % (
                graph.node[i]["label"], graph.node[j]["label"]
            )

            if label not in bag:
                bag[label] = 0.0
            bag[label] += 1.0

    return bag


def bag_of_shortest_paths(graph, maxlen=None):
    """ Build bag of shortest path for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=maxlen)

    bag = {}
    for i in paths:
        for j in paths[i]:
            path = map(lambda x: graph.node[x]["label"], paths[i][j])
            label = '-'.join(path)
            if label not in bag:
                bag[label] = 0.0
            bag[label] += 1.0

    return bag


def bag_of_cliques(graph, k):
    """ Build bag of k-cliques for graph """

    bag = {}
    for nodes in nx.k_clique_communities(graph, k):
        ns = map(lambda x: graph.node[x]["label"], nodes)
        label = '-'.join(sorted(ns))
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_strongly_connected_components(graph):
    """ Bag of strongly connected components """
    comp = nx.strongly_connected_components(graph)
    return bag_of_components(graph, comp)


def bag_of_weakly_connected_components(graph):
    """ Bag of weakly connected components """
    comp = nx.weakly_connected_components(graph)
    return bag_of_components(graph, comp)


def bag_of_biconnected_components(graph):
    """ Bag of bi-connected components """
    comp = nx.biconnected_components(graph)
    return bag_of_components(graph, comp)


def bag_of_attracting_components(graph):
    """ Bag of attracting components """
    comp = nx.attracting_components(graph)
    return bag_of_components(graph, comp)


def bag_of_components(graph, comp):
    """ Build bag of components for graph """

    bag = {}
    for nodes in comp:
        ns = map(lambda x: graph.node[x]["label"], nodes)
        label = '-'.join(sorted(ns))
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_to_fvec(bag, bits=24, fmap=None):
    """ Map bag to sparse feature vector """

    fvec = {}
    hashes = {}

    for key in bag:
        hash = utils.murmur3(key)
        dim = hash & (1 << bits) - 1
        sign = 2 * (hash >> 31) - 1

        if dim not in fvec:
            fvec[dim] = 0
        fvec[dim] += sign * bag[key]

        # Store dim-key mapping
        if fmap:
            if dim not in hashes:
                hashes[dim] = set()
            if key not in hashes[dim]:
                hashes[dim].add(key)

    return fvec, hashes if fmap else None
