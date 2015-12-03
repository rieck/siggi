#!/usr/bin/env python
# Siggie - A Simple Tool for Graph Embeddi
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import argparse
from multiprocessing import Pool
import fnmatch

import utils
import siggie

# Supported modes for embedding
modes = {
    0: "bag_of_nodes",
    1: "bag_of_edges",
    2: "bag_of_neighbors",
    3: "bag_of_weakly_connected_components",
    4: "bag_of_strong_connected_components",
    5: "bag_of_attracting_components",
    6: "bag_of_closure",
    7: "bag_of_weighted_closure",
    8: "bag_of_shortest_paths",
}

# Parse arguments
parser = argparse.ArgumentParser(description='Embed graphs in a vector space.')
parser.add_argument('-o', '--output', metavar='file', default="output.libsvm",
                    help='output file in libsvm format')
parser.add_argument('bundles', metavar='bundles', nargs='+',
                    help='graph bundles (DOT files in Zip archives)')
parser.add_argument('-b', '--bags', metavar='mode', default=0, type=int,
                    help='bag mode for embedding')
args = parser.parse_args()

# Initialize pool for multi-threading
pool = Pool()

# Loop over bundles on command line
for i, bundle in enumerate(args.bundles):
    print "Loading graphs from bundle %s" % bundle
    graphs = utils.load_dot_zip(bundle)

    for mode, func in modes.items():
        if args.bags == mode:
            print "Embedding using bag of %s" % func.replace("_", " ")

            # Get function from string
            possibles = globals().copy()
            possibles.update(locals())
            bags = pool.map(possibles.get(func), graphs)

    del graphs

    fvecs = pool.map(siggie.bag_to_fvec, bags)
    del bags

    label = 1
    if i == 0:
        print "Saving feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, label=label)
    else:
        print "Appending feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, label=label, append=True)
