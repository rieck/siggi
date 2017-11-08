# Siggi - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import networkx as nx
import string

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

# Global arguments
args = None


def add_arguments(parser):
    """ Add command-line arguments to partser """

    parser.add_argument('-b', '--bits', metavar='N', default=24, type=int,
                        help='set bits for feature hashing')
    parser.add_argument('-f', '--fmap', default=False, action='store_true',
                        help='store feature mapping in file')
    parser.add_argument('-l', '--minlen', metavar='N', default=3, type=int,
                        help='set minimum length of shortest paths')
    parser.add_argument('-L', '--maxlen', metavar='N', default=3, type=int,
                        help='set maximum length of shortest paths')
    parser.add_argument('-s', '--size', metavar='N', default=2, type=int,
                        help='set size of neighborhoods')
    parser.add_argument('-d', '--depth', metavar='N', default=5, type=int,
                        help='set depth of reachabilities')
    parser.add_argument('-n', '--norm', metavar='S', default='none',
                        help='set vector norm: l1, l2 or none')
    parser.add_argument('-M', '--map', metavar='S', default='count',
                        help='set map type: binary or count')
    parser.add_argument('-p', '--label', metavar='S', default='label',
                        help='set name of label property')


def set_args(pargs):
    """ Set global arguments structure """
    global args
    args = pargs


def node_label(node):
    """ Return the label of a node """

    output = []
    labels = map(string.strip, args.label.split(","))

    for label in labels:
        if label in node:
            output.append(str(node[label]))
        else:
            output.append('')

    return '|'.join(output)


def bag_name(m):
    """ Return the name and config of a bag mode """

    s = modes[m].replace("_", " ")
    s = s.replace("bag of", "bags of")

    if m == 2:
        s += " (size: %d)" % args.size
    elif m == 3:
        s += " (depth: %d)" % args.depth
    elif m == 4:
        s += " (min: %d, max: %d)" % (args.minlen, args.maxlen)
    return s


def bag_of_nodes(graph):
    """ Build bag of nodes from graph """

    bag = {}
    for i in graph.nodes():
        label = node_label(graph.node[i])
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_edges(graph):
    """ Build bag of edges from graph """

    bag = {}
    for i, j in graph.edges():
        n1 = node_label(graph.node[i])
        n2 = node_label(graph.node[j])
        label = "%s-%s" % (n1, n2)
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_neighborhoods(graph):
    """ Build bag of neighborhoods for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=args.size)

    bag = {}
    for i in paths:
        reachable = filter(lambda x: x != i, paths[i].keys())
        n = node_label(graph.node[i])
        ns = map(lambda x: node_label(graph.node[x]), reachable)
        label = "%s:%s" % (n, '-'.join(sorted(ns)))

        if label not in bag:
            bag[label] = 0.0
        bag[label] += 1.0

    return bag


def bag_of_reachabilities(graph):
    """ Build bag of reachabilities for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=args.depth)

    bag = {}
    for i in paths:
        reachable = filter(lambda x: x != i, paths[i].keys())
        if len(reachable) == 0:
            continue

        for j in reachable:
            n1 = node_label(graph.node[i])
            n2 = node_label(graph.node[j])
            label = "%s:%s" % (n1, n2)

            if label not in bag:
                bag[label] = 0.0
            bag[label] += 1.0

    return bag


def bag_of_shortest_paths(graph):
    """ Build bag of shortest path for graph """

    paths = nx.all_pairs_shortest_path(graph, cutoff=args.maxlen)

    bag = {}
    for i in paths:
        for j in paths[i]:
            path = map(lambda x: node_label(graph.node[x]), paths[i][j])
            if len(path) - 1 < args.minlen:
                continue

            label = '-'.join(path)
            if label not in bag:
                bag[label] = 0.0
            bag[label] += 1.0

    return bag


def bag_of_connected_components(graph):
    """ Bag of strongly connected components """
    comp = nx.strongly_connected_components(graph)
    return __bag_of_components(graph, comp)


def bag_of_attracting_components(graph):
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
        ns = map(lambda x: node_label(graph.node[x]), nodes)
        label = '-'.join(sorted(ns))
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_elementary_cycles(graph):
    """ Bag of elementary cycles """

    bag = {}
    for cycle in nx.simple_cycles(graph):
        ns = map(lambda x: node_label(graph.node[x]), cycle)

        # Determine smallest label and rotate cycle
        i = min(enumerate(ns), key=lambda x: x[1])[0]
        ns.extend(ns[:i])
        ns[:i] = []

        label = '-'.join(ns)
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_of_branchless_paths(graph):
    """ Bag of branchless paths """

    bag = {}
    for i in graph.nodes():
        if graph.out_degree(i) > 1:
            graph.remove_node(i)

    for nodes in nx.weakly_connected_components(graph):
        ns = map(lambda x: node_label(graph.node[x]), nodes)
        label = '-'.join(reversed(ns))
        if label not in bag:
            bag[label] = 0
        bag[label] += 1

    return bag


def bag_to_fvec(bag):
    """ Map bag to sparse feature vector """

    fvec = {}
    hashes = {}

    for key in bag:
        hash = utils.murmur3(key)
        dim = (hash & (1 << args.bits) - 1) + 1
        sign = 2 * (hash >> 31) - 1

        if dim not in fvec:
            fvec[dim] = 0
        fvec[dim] += sign * bag[key]

        # Store dim-key mapping
        if args.fmap:
            if dim not in hashes:
                hashes[dim] = set()
            if key not in hashes[dim]:
                hashes[dim].add(key)

    return fvec, hashes if args.fmap else None


def fvec_norm(fvec):
    """ Normalization of feature vector """

    mtype = args.map.lower()
    if mtype == "binary":
        for k in fvec.keys():
            fvec[k] = 1.0
    elif mtype != "count":
        raise Exception("Unknown map type '%s'" % mtype)

    norm = args.norm.lower()
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

