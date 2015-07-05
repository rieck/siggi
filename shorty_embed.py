#!/usr/bin/env python
# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import argparse
from multiprocessing import Pool
import fnmatch

import utils
import shorty

parser = argparse.ArgumentParser(
    description='Embed graphs in a vector space.'
)
parser.add_argument(
    '-o', '--output', metavar='file', default="output.libsvm",
    help='output file in libsvm format'
)
parser.add_argument(
    'bundles', metavar='bundle', nargs='+',
    help='graph bundles as zip archives'
)
parser.add_argument(
    '-b', '--bags', metavar='mode', default=0, type=int,
    help='bag mode for embedding'
)
parser.add_argument(
    '-n', '--negative', metavar='mask', default='malware*',
    help='file mask for bundles of negative class'
)
parser.add_argument(
    '-p', '--positive', metavar='mask', default='market*',
    help='file mask for bundles of positive class'
)

args = parser.parse_args()
pool = Pool()

for i, bundle in enumerate(args.bundles):
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
        print "Embedding using bag of weakly connected components"
        bags = pool.map(shorty.bag_of_weakly_connected_components, graphs)
    elif args.bags == 4:
        print "Embedding using bag of strongly connected components"
        bags = pool.map(shorty.bag_of_strongly_connected_components, graphs)
    elif args.bags == 5:
        print "Embedding using bag of attracting components"
        bags = pool.map(shorty.bag_of_attracting_components, graphs)
    elif args.bags == 6:
        print "Embedding using bag of closure"
        bags = pool.map(shorty.bag_of_closure, graphs)
    elif args.bags == 7:
        print "Embedding using bag of weighted closure"
        bags = pool.map(shorty.bag_of_weighted_closure, graphs)
    elif args.bags == 8:
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

    if i == 0:
        print "Saving feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, label=label)
    else:
        print "Appending feature vectors to %s" % args.output
        utils.save_libsvm(args.output, fvecs, label=label, append=True)
