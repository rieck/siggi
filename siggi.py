# Siggi - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

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
    7: "bag_of_branchless_paths",
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
    parser.add_argument('-n', '--norm', metavar='S', default='none',
                        help='set vector norm: l1, l2 or none')
    parser.add_argument('-M', '--map', metavar='S', default='count',
                        help='set map type: binary or count')


def bag_name(m, **kwargs):
    """ Return the name and config of a bag mode """

    s = modes[m].replace("_", " ")
    s = s.replace("bag of", "bags of")

    if m == 2:
        s += " (size: %d)" % kwargs["size"]
    elif m == 3:
        s += " (depth: %d)" % kwargs["depth"]
    elif m == 4:
        s += " (min: %d, max: %d)" % (kwargs["minlen"], kwargs["maxlen"])
    return s


def bag_of_nodes(graph, **kwargs):
    """ Build bag of nodes from graph """

    bag = {}
    for i in graph.nodes():
        label = graph.node[i]["label"]
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_edges(graph, **kwargs):
    """ Build bag of edges from graph """

    bag = {}
    for i, j in graph.edges():
        label = "%s-%s" % (graph.node[i]["label"], graph.node[j]["label"])
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_neighborhoods(graph, **kwargs):
    """ Build bag of neighborhoods for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=kwargs["size"])

    bag = {}
    for i in paths:
        reachable = filter(lambda x: x != i, paths[i].keys())
        ns = map(lambda x: graph.node[x]["label"], reachable)
        label = "%s:%s" % (graph.node[i]["label"], '-'.join(sorted(ns)))

        if label not in bag:
            bag[label] = 0.0
        bag[label] += 1.0

    return bag


def bag_of_reachabilities(graph, **kwargs):
    """ Build bag of reachabilities for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=kwargs["depth"])

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


def bag_of_shortest_paths(graph, **kwargs):
    """ Build bag of shortest path for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=kwargs["maxlen"])

    bag = {}
    for i in paths:
        for j in paths[i]:
            path = map(lambda x: graph.node[x]["label"], paths[i][j])
            if len(path) - 1 < kwargs["minlen"]:
                continue

            label = '-'.join(path)
            if label not in bag:
                bag[label] = 0.0
            bag[label] += 1.0

    return bag


def bag_of_connected_components(graph, **kwargs):
    """ Bag of strongly connected components """
    comp = nx.strongly_connected_components(graph)
    return __bag_of_components(graph, comp)


def bag_of_attracting_components(graph, **kwargs):
    """ Bag of attracting components """
    # Hack to deal with broken nx implementation
    if len(graph.node) == 0:
        return {}
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


def bag_of_elementary_cycles(graph, **kwargs):
    """ Bag of elementary cycles """

    bag = {}
    for cycle in nx.simple_cycles(graph):
        ns = map(lambda x: graph.node[x]["label"], cycle)

        # Determine smallest label and rotate cycle
        i = min(enumerate(ns), key=lambda x: x[1])[0]
        ns.extend(ns[:i])
        ns[:i] = []

        label = '-'.join(ns)
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_branchless_paths(graph, **kwargs):
    """ Bag of branchless paths """

    bag = {}
    for i in graph.nodes():
        if graph.out_degree(i) > 1:
            graph.remove_node(i)

    for nodes in nx.weakly_connected_components(graph):
        ns = map(lambda x: graph.node[x]["label"], nodes)
        label = '-'.join(reversed(ns))
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_to_fvec(bag, **kwargs):
    """ Map bag to sparse feature vector """

    fvec = {}
    hashes = {}

    for key in bag:
        hash = utils.murmur3(key)
        dim = (hash & (1 << kwargs["bits"]) - 1) + 1
        sign = 2 * (hash >> 31) - 1

        if dim not in fvec:
            fvec[dim] = 0
        fvec[dim] += sign * bag[key]

        # Store dim-key mapping
        if "fmap" in kwargs:
            if dim not in hashes:
                hashes[dim] = set()
            if key not in hashes[dim]:
                hashes[dim].add_string(key)

    return fvec, hashes if "fmap" in kwargs else None


def fvec_norm(fvec, **kwargs):
    """ Normalization of feature vector """

    mtype = kwargs["map"].lower()
    if mtype == "binary":
        for k in fvec.keys():
            fvec[k] = 1.0
    elif mtype != "count":
        raise Exception("Unknown map type '%s'" % mtype)

    norm = kwargs["norm"].lower()
    if norm == "l1" or norm == "manhattan":
        total = map(lambda x: abs(x), fvec.values())
        total = float(sum(total))
        for k in fvec.keys():
            fvec[k] /= total
    elif norm == "l2" or norm == "euclidean":
        total = map(lambda x: x * x, fvec.values())
        total = float(sum(total)) ** 0.5
        for k in fvec.keys():
            fvec[k] /= total
    elif norm != "none":
        raise Exception("Unknown vector norm '%s'" % norm)

    return fvec


def check_graph(graph, **kwargs):
    """ Check if a graph is suitable for analysis """

    for i in graph.nodes():
        if "label" not in graph.node[i]:
            raise Exception('Node %s is not labeled' % i)
        if len(graph.node[i]["label"]) == 0:
            raise Exception('Label of node %s is empty' % i)
