# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import sys
import networkx as nx
import utils
from collections import defaultdict


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


def bag_of_closure(graph, maxlen=None, weight_len=False):
    """ Build bag of transitive closure for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=maxlen)

    bag = {}
    for i in paths:
        for j in paths[i]:
            if i == j:
                continue
            label = "%s:%s" % (graph.node[i]["label"], graph.node[j]["label"])

            if label not in bag:
                bag[label] = 0.0
            if not weight_len:
                bag[label] += 1.0
            else:
                bag[label] += 1.0 / (len(paths[i][j]) - 1)

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


def bag_of_components(graph, type="strongly connected"):
    """ Build bag of components for graph """

    if type == "attracting":
        comp = nx.attracting_components(graph)
    elif type == "strongly connected":
        comp = nx.strongly_connected_components(graph)
    elif type == "weakly connected":
        comp = nx.weakly_connected_components(graph)
    elif type == "biconnected":
        comp = nx.biconnected_components(graph)
    else:
        raise Exception("Unknown connectivity type")

    bag = {}
    for nodes in comp:
        ns = map(lambda x: graph.node[x]["label"], nodes)
        label = '-'.join(sorted(ns))
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def floyd_warshall(graph, semiring=None, weight='weight'):
    """ Find all-pairs shortest path lengths using Floyd's algorithm. """

    # Adapted From NetworkX. Copyright (C) 2004-2012 by
    # Aric Hagberg <hagberg@lanl.gov>, Dan Schult <dschult@colgate.edu>
    # Pieter Swart <swart@lanl.gov> All rights reserved.  BSD license.

    if not semiring:
        semiring = {
            "plus": lambda x, y: x + y,
            "zero": 0.0,
            "prod": lambda x, y: min(x, y),
            "one": float("inf"),
        }

    # dictionary-of-dictionaries representation for dist and pred
    # use some defaultdict magick here
    # for dist the default is the floating point inf value
    dist = defaultdict(lambda: defaultdict(lambda: semiring["one"]))
    for u in graph:
        dist[u][u] = semiring["zero"]
    pred = defaultdict(dict)

    # initialize path distance dictionary to be the adjacency matrix
    # also set the distance to self to 0 (zero diagonal)
    undirected = not graph.is_directed()
    for u, v, d in graph.edges(data=True):
        e_weight = d.get(weight, 1.0)
        dist[u][v] = min(e_weight, dist[u][v])
        pred[u][v] = u
        if undirected:
            dist[v][u] = min(e_weight, dist[v][u])
            pred[v][u] = v

    for w in graph:
        for u in graph:
            for v in graph:
                a = semiring["plus"](dist[u][w], dist[w][v])
                b = dist[u][v]
                dist[u][v] = semiring["prod"](a, b)
                if dist[u][v] != b:
                    pred[u][v] = pred[w][v]

    return dict(pred), dict(dist)


def bag_to_fvec(bag, bits=24, hashs={}):
    """ Map bag to sparse feature vector """

    fvec = {}
    for key in bag:
        hash = utils.murmur3(key)
        dim = hash & (1 << bits) - 1
        sign = 2 * (hash >> 31) - 1

        if dim not in fvec:
            fvec[dim] = 0
        fvec[dim] += sign * bag[key]

        # Store dim-key mapping
        if dim not in hashs:
            hashs[dim] = []
        if key not in hashs[dim]:
            hashs[dim].append(key)

    return fvec
