#!/usr/bin/env python
# Siggie - A Simple Tool for Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import argparse
from functools import partial
from multiprocessing import Pool

import siggie
import utils

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
parser.add_argument('-l', '--label', metavar='R', default="^\d+",
                    help='set regex for labels in filenames')
parser.add_argument('-b', '--bits', metavar='N', default=24, type=int,
                    help='set bits for feature hashing')
args = parser.parse_args()

# Initialize pool for multi-threading
pool = Pool()

# Loop over bundles on command line
for i, bundle in enumerate(args.bundle):
    print "= Loading graphs from bundle %s" % bundle
    graphs, labels = utils.load_dot_zip(bundle, args.label)

    for mode, fname in siggie.modes.items():
        if args.mode == mode:
            print "= Embedding graphs using %s" % fname.replace("_", " ")
            bags = pool.map(getattr(siggie, fname), graphs)
            break
    del graphs

    # Convert bags to feature vectors
    print "= Converting bags to feature vectors"
    func = partial(siggie.bag_to_fvec, bits=args.bits)
    fvecs = pool.map(func, bags)
    del bags

    if i == 0:
        print "= Saving feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, labels)
    else:
        print "= Appending feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, labels, append=True)
