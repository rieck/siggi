#!/usr/bin/env python
# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import os
import argparse
from multiprocessing import Pool
import fnmatch

import utils
import shorty

parser = argparse.ArgumentParser(
    description='Embed graphs in a vector space.'
)
parser.add_argument(
    '--output', metavar='file', default="output.libsvm",
    help='output file in libsvm format'
)
parser.add_argument(
    'bundles', metavar='bundle', nargs='+',
    help='graph bundles as zip archives'
)
parser.add_argument(
    '--bags', metavar='mode', default=0, type=int,
    help='bags for embedding: '
         '0 = nodes, 1 = edges, 2 = neighbors, 3 = weak components, '
         '4 = attracting components, 5 = closure, 6 = weighted closure '
         '7 = shortest paths'
)
parser.add_argument(
    '--negative', metavar='mask', default='malware*',
    help='file mask for bundles of negative class'
)
parser.add_argument(
    '--positive', metavar='mask', default='market*',
    help='file mask for bundles of positive class'
)

args = parser.parse_args()
pool = Pool()

for bundle in args.bundles:
    print "Loading DOT graphs from bundle %s" % bundle
    graphs = utils.load_dot_zip(bundle)

    if args.bags == 0:
        print "Embedding using bag of nodes"
        bags = pool.map(shorty.bag_of_nodes, graphs)
    elif args.bags == 1:
        print "Embedding using bag of edges"
        bags = pool.map(shorty.bag_of_edges, graphs)
    elif args.bags == 2:
        print "Embedding using bag of neighbors"
        bags = pool.map(shorty.bag_of_neighbors, graphs)
    elif args.bags == 3:
        print "Embedding using bag of weak components"
        func = lambda x: shorty.bag_of_components(x, "weakly connected")
        bags = pool.map(func, graphs)
    elif args.bags == 4:
        print "Embedding using bag of attracting components"
        func = lambda x: shorty.bag_of_components(x, "attracting")
        bags = pool.map(func, graphs)
    elif args.bags == 5:
        print "Embedding using bag of closure"
        bags = pool.map(shorty.bag_of_closure, graphs)
    elif args.bags == 6:
        print "Embedding using bag of weighted closure"
        func = lambda x: shorty.bag_of_closure(x, weight_len=True)
        bags = pool.map(func, graphs)
    elif args.bags == 7:
        print "Embedding using bag of shortest paths"
        bags = pool.map(shorty.bag_of_shortest_paths, graphs)
    else:
        raise Exception("Unknown bag mode %d" % args.bags)
    del graphs

    fvecs = pool.map(shorty.bag_to_fvec, bags)
    del bags

    label = None
    if fnmatch.fnmatch(bundle, args.negative):
        label = -1
    elif fnmatch.fnmatch(bundle, args.positive):
        label = +1

    if not os.path.exists(args.output):
        print "Saving feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, label=label)
    else:
        print "Appending feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, label=label, append=True)
