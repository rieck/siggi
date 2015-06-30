# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import os
import gzip
import pickle
import progressbar as pb
import networkx as nx
import zipfile as zf


def pbmap(func, list):
    """ Map function with progressbar """

    progress = pb.ProgressBar()
    out = []
    for item in progress(list):
        out.append(func(item))

    return out


def load_fcg(path):
    """ Load graphs in FCG format (see Adagio by H. Gascon) """

    graphs = []
    progress = pb.ProgressBar()

    # Read files from directory in original "pz" format"
    if os.path.isdir(path):
        for file in progress(os.listdir(path)):
            fn = os.path.join(path, file)
            if os.path.splitext(file)[1] != ".pz":
                continue

            g = pickle.loads(gzip.open(fn).read())
            g = unify_fcg(g)
            graphs.append(g)
    # Read files from zip archive in unpacked "fcg" format
    else:
        z = zf.ZipFile(path)
        for file in progress(z.namelist()):
            if os.path.splitext(file)[1] != ".fcg":
                continue

            g = pickle.loads(z.open(file).read())
            g = unify_fcg(g)
            graphs.append(g)

    return graphs


def unify_fcg(g):
    """ Unify layout of FCG format """

    # Map nodes to indices for simplicity
    mapping = dict(zip(g.nodes(), range(len(g.nodes()))))
    g = nx.relabel_nodes(g, mapping)

    # Add original node labels and fix label
    inverse = {v: k for k, v in mapping.items()}
    for key in g.nodes():
        g.node[key]["function"] = inverse[key]
        label = g.node[key]["label"]
        g.node[key]["label"] = ''.join(map(str, label))

    return g


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
