# Siggie - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import sys
import networkx as nx

import utils


# Supported modes for bags
modes = {
    0: "bag_of_nodes",
    1: "bag_of_edges",
    2: "bag_of_neighborhoods",
    3: "bag_of_reachabilities",
    4: "bag_of_shortest_paths",
    5: "bag_of_connected_components",
    6: "bag_of_attracting_components",
}


def add_arguments(parser):
    """ Add command-line arguments to partser """

    parser.add_argument('-b', '--bits', metavar='N', default=24, type=int,
                        help='set bits for feature hashing')
    parser.add_argument('-f', '--fmap', metavar='F', default=None,
                        help='store feature mapping in file')
    parser.add_argument('-l', '--minlen', metavar='N', default=3, type=int,
                        help='set minimum length of shortest paths')
    parser.add_argument('-L', '--maxlen', metavar='N', default=3, type=int,
                        help='set maximum length of shortest paths')
    parser.add_argument('-s', '--size', metavar='N', default=1, type=int,
                        help='set size of neighborhoods')
    parser.add_argument('-d', '--depth', metavar='N', default=5, type=int,
                        help='set depth of reachabilities')

def mode_name(mode, args):
    """ Return the name and config of a bag mode """

    s = modes[mode].replace("_", " ")
    if mode == 2:
        s += " (size: %d)" % args.size
    elif mode == 3:
        s += " (depth: %d)" % args.depth
    elif mode == 4:
        s += " (min: %d, max: %d)" % (args.minlen, args.maxlen)
    return s


def bag_of_nodes(graph, args):
    """ Build bag of nodes from graph """

    bag = {}
    for i in graph.nodes():
        label = graph.node[i]["label"]
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_edges(graph, args):
    """ Build bag of edges from graph """

    bag = {}
    for i, j in graph.edges():
        label = "%s-%s" % (graph.node[i]["label"], graph.node[j]["label"])
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_neighborhoods(graph, args):
    """ Build bag of neighborhoods for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=args.size)

    bag = {}
    for i in paths:
        reachable = filter(lambda x: x != i, paths[i].keys())
        ns = map(lambda x: graph.node[x]["label"], reachable)
        label = "%s:%s" % (graph.node[i]["label"], '-'.join(sorted(ns)))

        if label not in bag:
            bag[label] = 0.0
        bag[label] += 1.0

    return bag


def bag_of_reachabilities(graph, args):
    """ Build bag of reachabilities for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=args.depth)

    bag = {}
    for i in paths:
        reachable = filter(lambda x: x != i, paths[i].keys())
        if len(reachable) == 0:
            continue

        for j in reachable:
            label = "%s:%s" % (
                graph.node[i]["label"], graph.node[j]["label"]
            )

            if label not in bag:
                bag[label] = 0.0
            bag[label] += 1.0

    return bag


def bag_of_shortest_paths(graph, args):
    """ Build bag of shortest path for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=args.maxlen)

    bag = {}
    for i in paths:
        for j in paths[i]:
            path = map(lambda x: graph.node[x]["label"], paths[i][j])
            if len(path) - 1 < args.minlen:
                continue

            label = '-'.join(path)
            if label not in bag:
                bag[label] = 0.0
            bag[label] += 1.0

    return bag


def bag_of_connected_components(graph, args):
    """ Bag of strongly connected components """
    comp = nx.strongly_connected_components(graph)
    return __bag_of_components(graph, comp)


def bag_of_attracting_components(graph, args):
    """ Bag of attracting components """
    comp = nx.attracting_components(graph)
    return __bag_of_components(graph, comp)


def __bag_of_components(graph, comp):
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
