#!/usr/bin/env python
# Siggi - Feature Hashing for Labeled Graphs
# (c) 2016 Konrad Rieck (konrad@mlsec.org)

import StringIO
import argparse
import gzip
import os
import pickle
import tempfile
from multiprocessing import Pool
import networkx as nx

import utils


def load_pz_file(filename):
    """ Loads a pz object from a file. (See Adagio by Gascon) """

    file = gzip.GzipFile(filename, 'rb')
    buffer = ""
    while True:
        data = file.read()
        if data == "":
            break
        buffer += data
    object = pickle.loads(buffer)
    file.close()
    return object


def load_pz_dir(dir):
    """ Loads pz objects from a directory. (See Adagio by Gascon) """

    pool = Pool()
    files = map(lambda x: os.path.join(dir, x), os.listdir(dir))
    files = filter(lambda x: x.endswith(".pz"), files)
    objects = pool.map(load_pz_file, files)
    pool.close()
    pool.join()
    return objects


def __networkx_to_graphml(graph):
    """ Convert a networkx object to a graphml string """

    out = StringIO.StringIO()
    nx.write_graphml(graph, out)
    graphml = out.getvalue()
    out.close()
    return graphml


def __networkx_to_dot(graph):
    """ Convert a networkx object to a dot string """

    _, tf = tempfile.mkstemp()
    nx.drawing.nx_agraph.write_dot(graph, tf)
    dot = open(tf).read()
    os.unlink(tf)
    return dot


def convert_networkx(graphs, format="graphml"):
    """ Convert networkx objects to graphml strings """

    if format == "graphml":
        func = __networkx_to_graphml
    elif format == "dot":
        func = __networkx_to_dot
    else:
        raise Exception("Unknown bundle format: " + format)

    # Parallel conversion
    pool = Pool()
    bundle = pool.map(func, graphs)
    pool.close()
    pool.join()
    return bundle


# Parse arguments
parser = argparse.ArgumentParser(
    description='Siggi - Convert graph formats to graph bundles.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('bundle', metavar='bundle', type=str,
                    help='graph bundle (zip archive of dot/graphml files)')
parser.add_argument('-p', '--pz', metavar='dir', type=str,
                    help='create bundle from directory of pz files')
parser.add_argument('-f', '--format', metavar='format', type=str,
                    help='format of graph bundle. default: dot', default="dot")
parser.add_argument('-l', '--label', metavar='label', type=int,
                    help='numeric label for graphs. default: 0', default=0)

args = parser.parse_args()

if args.pz:
    graphs = load_pz_dir(args.pz)
    graphs = convert_networkx(graphs, format=args.format)
    utils.save_graph_zip(args.bundle, graphs, format=args.format, label=args.label)
