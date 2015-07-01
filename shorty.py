# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import utils
import sys


def bag_of_labels(graph):
    """ Build bag of labels from graph """

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


graphs = utils.load_fcg_zip(sys.argv[1])
utils.save_dot_zip(graphs, "foobar.zip")
graphs = utils.load_dot_zip("foobar.zip")
