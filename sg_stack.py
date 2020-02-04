#!/usr/bin/env python2

import argparse

import utils

# Parse arguments
parser = argparse.ArgumentParser(
    description='Siggi - Stack Feature Spaces.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('input', metavar='libsvm', nargs='+',
                    help='input files in libsvm format')
parser.add_argument('-o', '--output', metavar='F', default="output.libsvm",
                    help='set libsvm output file')

args = parser.parse_args()
fvecs = None
labels = None

for infile in args.input:
    print "= Loading feature vectors from %s" % infile
    in_fvecs, in_labels = utils.load_libsvm(infile)

    if not fvecs:
        fvecs = in_fvecs
        labels = in_labels
    else:
        fvecs = utils.stack_fvecs(fvecs, in_fvecs)
        assert (labels == in_labels)

    # This is not necessary. Remove if too slow
    print "= Stacked feature space with %d dimensions" % (
        max(map(max, fvecs))
    )

print "= Saving feature vectors to %s" % args.output
utils.save_libsvm(args.output, fvecs, labels)
