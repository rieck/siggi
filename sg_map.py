#!/usr/bin/env python2
# Siggi - Feature Hashing for Labeled Graphs
# (c) 2015, 2017 Konrad Rieck (konrad@mlsec.org)

import argparse
from multiprocessing import Pool

import siggi
import utils

# Parse arguments
parser = argparse.ArgumentParser(
    description='Siggi - Feature Hashing for Labeled Graphs.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('bundle', metavar='bundle', nargs='+',
                    help='graph bundle (zip archive of dot/graphml files)')
parser.add_argument('-o', '--output', metavar='F', default="output.libsvm",
                    help='set libsvm output file')
parser.add_argument('-m', '--mode', metavar='N', default=0, type=int,
                    help='set bag mode for feature hashing')
parser.add_argument('-r', '--regex', metavar='R', default="^\d+",
                    help='set regex for labels in filenames')
parser.add_argument('-c', '--chunks', metavar='N', default=1, type=int,
                    help='set number of chunks to process')
siggi.add_arguments(parser)

args = parser.parse_args()
siggi.set_args(args)

# Initialize pool for multi-threading
pool = Pool()

# Loop over bundles on command line
for i, bundle in enumerate(args.bundle):
    # Get entries and create chunks
    entries = utils.list_bundle(bundle)
    chunks = utils.chunkify_entries(entries, args.chunks)
    for j, chunk in enumerate(chunks):

        print "= Loading %d graphs from bundle %s" % (len(chunk), bundle)
        graphs, labels = utils.load_bundle(bundle, args.regex, chunk=chunk)

        print "= Extracting %s from graphs" % siggi.bag_name(args.mode)
        func = getattr(siggi, siggi.modes[args.mode])
        bags = pool.map(func, graphs)
        del graphs

        # Convert bags to feature vectors
        print "= Hashing bags to feature vectors (%d bits)" % args.bits
        items = pool.map(siggi.bag_to_fvec, bags)
        fvecs, fmaps = zip(*items)
        del bags

        # Normalizing feature vectors
        print "= Normalizing feature vectors (%s, %s)" % (args.map, args.norm)
        fvecs = pool.map(siggi.fvec_norm, fvecs)

        if i == 0 and j == 0:
            print "= Saving feature vectors to %s" % args.output
            utils.save_libsvm(args.output, fvecs, labels)
        else:
            print "= Appending feature vectors to %s" % args.output
            utils.save_libsvm(args.output, fvecs, labels, append=True)

if args.fmap:
    print "= Saving feature map to %s" % args.fmap
    utils.save_fmap(args.fmap, fmaps)

