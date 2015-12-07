#!/usr/bin/env python
# Siggie - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import argparse
import random
import time
from functools import partial
from multiprocessing import Pool

import numpy as np

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
parser.add_argument('-t', '--time', metavar='N', default=1, type=float,
                    help='number of seconds to benchmark')
siggie.add_arguments(parser)
args = parser.parse_args()
kwargs = vars(args)

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
        func = partial(getattr(siggie, fname), **kwargs)
        bag = func(graph)
        fvec = siggie.bag_to_fvec(bag, **kwargs)
        times.append(time.time() - start)

    speed = float(len(times)) / np.sum(times)
    print "  Mode: %d | %5.0f graphs/s | %5.2f ms/graph | +/- %5.2f" % (
        mode, speed, 1000 * np.mean(times), 1000 * np.std(times)
    )
