#!/usr/bin/env python
# Siggie - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import argparse
import time
import random
import numpy as np
from functools import partial
from multiprocessing import Pool

import siggie
import utils

# Parse arguments
parser = argparse.ArgumentParser(
    description='Benchmark feature hashing.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('bundle', metavar='bundle', nargs='+',
                    help='graph bundle (zip archive of DOT files)')
parser.add_argument('-m', '--mode', metavar='N', default=-1, type=int,
                    help='set bag mode for feature hashing')
parser.add_argument('-t', '--time', metavar='N', default=2, type=float,
                    help='number of seconds to benchmark')
parser.add_argument('-b', '--bits', metavar='N', default=24, type=int,
                    help='set bits for feature hashing')
parser.add_argument('-l', '--maxlen', metavar='N', default=3, type=int,
                    help='set maximum length of paths')
parser.add_argument('-s', '--size', metavar='N', default=1, type=int,
                    help='set size of neighborhoods')
parser.add_argument('-d', '--depth', metavar='N', default=5, type=int,
                    help='set depth of reachabilities')

args = parser.parse_args()

# Initialize pool for multi-threading
pool = Pool()

# Loop over bundles on command line
testset = []
for i, bundle in enumerate(args.bundle):
    print "= Loading graphs from bundle %s" % bundle
    graphs, _ = utils.load_dot_zip(bundle)
    testset.extend(graphs)

if args.mode == -1:
    modes = siggie.modes.items()
else:
    modes = [(args.mode, siggie.modes[args.mode])]

print "= Benchmarking modes for %g seconds" % args.time
for mode, fname in modes:
    times = []
    while np.sum(times) < args.time:
        graph = random.choice(testset)

        start = time.time()
        func = partial(getattr(siggie, fname), args=args)
        bag = func(graph)
        fvec = siggie.bag_to_fvec(bag, bits=args.bits)
        times.append(time.time() - start)

    speed = float(len(times)) / np.sum(times)
    print "  representation: %s" % siggie.mode_name(mode, args)
    print "  mode: %d | %5.0f graphs/s | %5.2f ms/graph | +/- %5.2f" % (
        mode, speed, 1000 * np.mean(times), 1000 * np.std(times)
    )
