# Siggi - Feature Hashing for Labeled Graph
# (c) 2015-2016 Konrad Rieck (konrad@mlsec.org)

import json
import os
import re
import zipfile as zf
from functools import partial
from multiprocessing import Pool

import networkx as nx
import pygraphviz as pg


def load_graph_zip(filename, regex="^\d+"):
    """ Load graphs from zip archive """

    pool = Pool()
    archive = zf.ZipFile(filename)

    entries = [(archive, entry) for entry in archive.namelist()]
    func = partial(load_graph_entry, regex=re.compile(regex))
    items = pool.map(func, entries)
    items = filter(lambda (g, l): g is not None, items)
    graphs, labels = zip(*items)

    archive.close()
    pool.close()
    pool.join()

    return graphs, labels


def save_graph_zip(filename, graphs, format="graphml", label=0):
    """ Save graphs to zip archive """

    archive = zf.ZipFile(filename, "w", zf.ZIP_DEFLATED)
    # This should be parallized one day
    for (i, graph) in enumerate(graphs):
        fname = "%d_%.6d.%s" % (label, i, format)
        archive.writestr(fname, graph)
    archive.close()


def load_graph_entry((archive, entry), regex):
    """ Load one graph from zip archive """

    # Determine label
    match = regex.match(os.path.basename(entry))
    if match and len(match.group(0)) > 0:
        label = int(match.group(0))
    else:
        label = 0

    if entry.endswith(".dot"):
        graph = pg.AGraph(archive.open(entry).read())
        return nx.from_agraph(graph), label
    elif entry.endswith(".graphml"):
        graph = nx.read_graphml(archive.open(entry))
        return graph, label
    else:
        return None, 0


def save_libsvm(filename, fvecs, labels, append=False):
    """ Save feature vectors to libsvm file """

    if not append:
        f = open(filename, "w")
    else:
        f = open(filename, "a")

    for fvec, label in zip(fvecs, labels):
        f.write("%d" % label)
        for dim in sorted(fvec):
            if abs(fvec[dim]) < 1e-9:
                continue
            f.write(" %d:%g" % (dim, fvec[dim]))
        f.write("\n")

    f.close()


def save_fmap(filename, fmaps):
    """ Save feature map in json format """

    # Merge feature maps from concurrent runs
    final = fmaps[0]

    for fm in fmaps[1:]:
        for k in fm:
            if k not in final:
                final[k] = fm[k]
            else:
                final[k].union(fm[k])

    # Convert to lists
    final.update({k: list(v) for k, v in final.iteritems()})
    json.dump(final, open(filename, "w"))


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


def mean(data):
    """ Simple mean function. Adapted from Python 3.4 """
    return sum(data) / float(len(data))


def std(data):
    """ Simple std function. Adapted from Python 3.4 """
    m = mean(data)
    ss = sum((x - m) ** 2 for x in data)
    s = ss / float(len(data))
    return s ** 0.5
