# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import pickle
import zipfile as zf
from multiprocessing import Pool

import pygraphviz as pg
import networkx as nx


def load_fcg_zip(filename):
    """ Load FCG graphs from zip archive """

    pool = Pool()
    archive = zf.ZipFile(filename)
    entries = [(archive, entry) for entry in archive.namelist()]

    graphs = pool.map(load_fcg_entry, entries)

    pool.close()
    pool.join()
    archive.close()

    return filter(lambda g: g, graphs)


def load_fcg_entry((archive, entry)):
    """ Load one FCG graph from zip archive """

    if entry.endswith("/") or not entry.endswith(".fcg"):
        return None

    g = pickle.loads(archive.open(entry).read())

    # Map nodes to indices for simplicity
    mapping = dict(zip(g.nodes(), range(len(g.nodes()))))
    g = nx.relabel_nodes(g, mapping)

    # Add original node labels and fix label
    inverse = {v: k for k, v in mapping.items()}
    for key in g.nodes():
        obj = ''.join(inverse[key][:-1]).decode("ascii", "ignore")
        g.node[key]["obj"] = obj
        label = g.node[key]["label"]
        g.node[key]["label"] = ''.join(map(str, label))

    return g


def load_dot_zip(filename):
    """ Load DOT graphs from zip archive """

    pool = Pool()
    archive = zf.ZipFile(filename)

    entries = [(archive, entry) for entry in archive.namelist()]
    graphs = pool.map(load_dot_entry, entries)

    archive.close()
    pool.close()
    pool.join()

    return filter(lambda g: g, graphs)


def load_dot_entry((archive, entry)):
    """ Load one DOT graph from zip archive """

    if entry.endswith("/") or not entry.endswith(".dot"):
        return None

    dot = pg.AGraph(archive.open(entry).read())
    return nx.from_agraph(dot)


def save_dot_zip(graphs, filename):
    """ Save DOT graphs to zip archive """

    archive = zf.ZipFile(filename, "w", zf.ZIP_DEFLATED)

    for i, g in enumerate(graphs):
        dot = nx.to_agraph(g)
        archive.writestr("%.7d.dot" % i, dot.to_string())

    archive.close()


def save_libsvm(filename, fvecs, label):
    """ Save feature vectors to libsvm file """

    f = open(filename, "w")

    for fvec in fvecs:
        f.write("%d" % label)
        for dim in sorted(fvec):
            if fvec[dim] < 1e-9:
                continue
            f.write(" %d:%g" % (dim, fvec[dim]))
        f.write("\n")

    f.close()


def murmur3(data, seed=0):
    """ Implementation of Murmur 3 hash by Maurus Decimus """

    c1 = 0xcc9e2d51
    c2 = 0x1b873593

    length = len(data)
    h1 = seed
    rend = (length & 0xfffffffc)  # round down to 4 byte block
    for i in range(0, rend, 4):
        # little endian load order
        k1 = (ord(data[i]) & 0xff) | ((ord(data[i + 1]) & 0xff) << 8) | \
             ((ord(data[i + 2]) & 0xff) << 16) | (ord(data[i + 3]) << 24)
        k1 *= c1
        k1 = (k1 << 15) | ((k1 & 0xffffffff) >> 17)  # ROTL32(k1,15)
        k1 *= c2

        h1 ^= k1
        h1 = (h1 << 13) | ((h1 & 0xffffffff) >> 19)  # ROTL32(h1,13)
        h1 = h1 * 5 + 0xe6546b64

    # tail
    k1 = 0

    val = length & 0x03
    if val == 3:
        k1 = (ord(data[rend + 2]) & 0xff) << 16
    # fall through
    if val in [2, 3]:
        k1 |= (ord(data[rend + 1]) & 0xff) << 8
    # fall through
    if val in [1, 2, 3]:
        k1 |= ord(data[rend]) & 0xff
        k1 *= c1
        k1 = (k1 << 15) | ((k1 & 0xffffffff) >> 17)  # ROTL32(k1,15)
        k1 *= c2
        h1 ^= k1

    # finalization
    h1 ^= length

    # fmix(h1)
    h1 ^= ((h1 & 0xffffffff) >> 16)
    h1 *= 0x85ebca6b
    h1 ^= ((h1 & 0xffffffff) >> 13)
    h1 *= 0xc2b2ae35
    h1 ^= ((h1 & 0xffffffff) >> 16)

    return h1 & 0xffffffff
