# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import os
import gzip
import pickle
from tqdm import *
import networkx as nx
import zipfile as zf


def tmap(func, list, desc):
    """ Map function with progressbar """

    out = []
    for item in tqdm(list, desc):
        out.append(func(item))

    return out


def load_fcg_dir(dir):
    """ Load graphs in FCG format (see Adagio by H. Gascon) """

    graphs = []
    for fn in tqdm(os.listdir(dir), "Loading"):
        path = os.path.join(dir, fn)
        # Load file in fcg format
        if os.path.splitext(fn)[1] == ".fcg":
            g = pickle.loads(open(path).read())
        # Load file in pz format
        elif os.path.splitext(fn)[1] == ".pz":
            g = pickle.loads(gzip.open(path).read())
        else:
            continue

        g = unify_fcg(g)
        graphs.append(g)

    return graphs


def load_fcg_zip(zfile):
    """ Load graphs in FCG format from zip archive """

    graphs = []
    z = zf.ZipFile(zfile)
    for fn in tqdm(z.namelist(), "Loading"):
        if fn.endswith("/"):
            continue
        g = pickle.loads(z.open(fn).read())
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


def save_libsvm(fn, fvecs, label):
    f = open(fn, "w")

    for fvec in tqdm(fvecs, "Saving"):
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
