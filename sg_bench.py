#!/usr/bin/env python
# Siggi - Feature Hashing for Labeled Graphs
# (c) 2015, 2017 Konrad Rieck (konrad@mlsec.org)

import argparse
import random
import time
from multiprocessing import Pool

import siggi
import utils

# Parse arguments
parser = argparse.ArgumentParser(
    description='Siggi - Benchmark Tests for Feature Hashing.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('bundle', metavar='bundle', nargs='+',
                    help='graph bundle (zip archive of dot/graphml files)')
parser.add_argument('-m', '--mode', metavar='N', default=-1, type=int,
                    help='set bag mode for feature hashing')
parser.add_argument('-t', '--time', metavar='N', default=1, type=float,
                    help='number of seconds to benchmark')
parser.add_argument('-r', '--ratio', metavar='R', default=1, type=float,
                    help='sample ratio to use for benchmark')
siggi.add_arguments(parser)
args = parser.parse_args()
siggi.set_args(args)

# Initialize pool for multi-threading
pool = Pool()

# Loop over bundles on command line
testset = []
for i, bundle in enumerate(args.bundle):
    print "= Loading graphs from bundle %s" % bundle
    entries = utils.list_bundle(bundle)
    random.shuffle(entries)
    sample = entries[:int(args.ratio * len(entries))]

    graphs, _ = utils.load_bundle(bundle, chunk=sample)
    testset.extend(graphs)

if args.mode == -1:
    modes = siggi.modes.items()
else:
    modes = [(args.mode, siggi.modes[args.mode])]

print "= Benchmarking modes for %g seconds" % args.time
for mode, fname in modes:
    times = []
    while sum(times) < args.time:
        start = time.time()
        graph = random.choice(testset)

        # Compute feature hashing
        func = getattr(siggi, fname)
        bag = func(graph)
        fvec = siggi.bag_to_fvec(bag)
        fvec = siggi.fvec_norm(fvec)

        times.append(time.time() - start)

    speed = float(len(times)) / sum(times)
    print "  Mode: %d | %5.0f graphs/s | %7.2f ms/graph | +/- %5.2f" % (
        mode, speed, 1000 * utils.mean(times), 1000 * utils.std(times)
    )
