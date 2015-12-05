#!/usr/bin/env python
# Siggie - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import argparse
from functools import partial
from multiprocessing import Pool

import siggie
import utils

# Parse arguments
parser = argparse.ArgumentParser(
    description='Map graphs to vectors.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('bundle', metavar='bundle', nargs='+',
                    help='graph bundle (zip archive of DOT files)')
parser.add_argument('-o', '--output', metavar='F', default="output.libsvm",
                    help='set output file')
parser.add_argument('-m', '--mode', metavar='N', default=0, type=int,
                    help='set bag mode for feature hashing')
parser.add_argument('-r', '--regex', metavar='R', default="^\d+",
                    help='set regex for labels in filenames')
parser.add_argument('-b', '--bits', metavar='N', default=24, type=int,
                    help='set bits for feature hashing')
parser.add_argument('-f', '--fmap', metavar='F', default=None,
                    help='store feature mapping in file')
parser.add_argument('-l', '--maxlen', metavar='N', default=3, type=int,
                    help='set maximum length of paths')
args = parser.parse_args()

# Initialize pool for multi-threading
pool = Pool()

# Loop over bundles on command line
for i, bundle in enumerate(args.bundle):
    print "= Loading graphs from bundle %s" % bundle
    graphs, labels = utils.load_dot_zip(bundle, args.regex)

    for mode, fname in siggie.modes.items():
        if args.mode == mode:
            print "= Hashing graphs using %s" % fname.replace("_", " ")
            func = getattr(siggie, fname)
            if mode in [6, 7, 8]:
                func = partial(func, maxlen=args.maxlen)
            bags = pool.map(func, graphs)
            break
    del graphs

    # Convert bags to feature vectors
    print "= Converting bags to feature vectors"
    func = partial(siggie.bag_to_fvec, bits=args.bits, fmap=args.fmap)
    items = pool.map(func, bags)
    fvecs, fmaps = zip(*items)
    del bags

    if i == 0:
        print "= Saving feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, labels)
    else:
        print "= Appending feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, labels, append=True)

if args.fmap:
    print "= Saving feature map to %s" % args.fmap
    utils.save_fmap(args.fmap, fmaps)
