# Siggie - Feature Hashing for Labeled Graph
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import json
import os
import re
import zipfile as zf
from functools import partial
from multiprocessing import Pool

import networkx as nx
import pygraphviz as pg


def load_dot_zip(filename, regex="^$"):
    """ Load DOT graphs from zip archive """

    pool = Pool()
    archive = zf.ZipFile(filename)

    entries = [(archive, entry) for entry in archive.namelist()]
    func = partial(load_dot_entry, regex=re.compile(regex))
    items = pool.map(func, entries)
    items = filter(lambda (g, l): g is not None, items)
    graphs, labels = zip(*items)

    archive.close()
    pool.close()
    pool.join()

    return graphs, labels


def load_dot_entry((archive, entry), regex="^\d+"):
    """ Load one DOT graph from zip archive """

    if entry.endswith("/") or not entry.endswith(".dot"):
        return None, 0

    dot = pg.AGraph(archive.open(entry).read())
    match = regex.match(os.path.basename(entry))
    label = int(match.group(0)) if match else 0

    return nx.from_agraph(dot), label


def save_dot_zip(graphs, filename):
    """ Save DOT graphs to zip archive """

    archive = zf.ZipFile(filename, "w", zf.ZIP_DEFLATED)

    for i, g in enumerate(graphs):
        dot = nx.to_agraph(g)
        archive.writestr("%.7d.dot" % i, dot.to_string())

    archive.close()


def save_libsvm(filename, fvecs, labels, append=False):
    """ Save feature vectors to libsvm file """

    if not append:
        f = open(filename, "w")
    else:
        f = open(filename, "a")

    for fvec, label in zip(fvecs, labels):
        f.write("%d" % label)
        for dim in sorted(fvec):
            if fvec[dim] < 1e-9:
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
