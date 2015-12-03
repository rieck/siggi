#!/usr/bin/env python
# Siggie - A Simple Tool for Graph Embeddi
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import argparse
from itertools import repeat
from multiprocessing import Pool

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
parser = argparse.ArgumentParser(
    description='Embed graphs in a vector space.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('bundle', metavar='bundle', nargs='+',
                    help='graph bundle (zip archive of DOT files)')
parser.add_argument('-o', '--output', metavar='F', default="output.libsvm",
                    help='set output file')
parser.add_argument('-m', '--mode', metavar='N', default=0, type=int,
                    help='set bag mode for embedding')
parser.add_argument('-l', '--label', metavar='R', default="^\d+_",
                    help='set regex for labels in filenames')
parser.add_argument('-b', '--bits', metavar='N', default=24, type=int,
                    help='set bits for feature hashing')
args = parser.parse_args()

# Initialize pool for multi-threading
pool = Pool()

# Loop over bundles on command line
for i, bundle in enumerate(args.bundle):
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

    # Convert bags to feature vectors
    fvecs = pool.map(siggie.bag_to_fvec, bags, repeat(args.bits))
    del bags

    label = 1   # Fixme
    if i == 0:
        print "Saving feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, label=label)
    else:
        print "Appending feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, label=label, append=True)
