#!/usr/bin/env python
# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import os
import argparse

import utils

parser = argparse.ArgumentParser(
    description='Convert and bundle graph representations.'
)
parser.add_argument(
    '-d', '--fcg2dot', action='store_true', default=False,
    help='convert FCG graph bundles to DOT graph bundles'
)
parser.add_argument(
    'bundles', metavar='bundle', nargs='+',
    help='graph bundles as zip archives'
)
args = parser.parse_args()

for bundle in args.bundles:
    base, ext = os.path.splitext(bundle)

    if ext != ".zip":
        print "Skipping %s. Not a bundle" % bundle
        continue

    # FCG to DOT conversion
    if args.fcg2dot:
        nf = "%s-dot%s" % (base, ext)
        if base.endswith("-dot"):
            print "Skipping %s. Already a DOT bundle" % bundle
            continue
        if os.path.exists(nf):
            print "Skipping %s. DOT bundle present" % bundle
            continue

        print "Loading FCG graphs from bundle %s" % bundle
        graphs = utils.load_fcg_zip(bundle)

        print "Saving DOT graphs to bundle %s" % nf
        utils.save_dot_zip(graphs, nf)
        del graphs
