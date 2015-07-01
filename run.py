#!/usr/bin/env python

import sys
import shorty
import utils
import os

for mode in "bol", "boe", "bon":
    for filename in sys.argv[1:]:

        graphs = utils.load_fcg_zip(filename)
        bags = utils.tmap(shorty.bag_of_neighbors, graphs, "Embedding")
        fvecs = utils.tmap(shorty.bag_to_fvec, bags, "Conversion")

        if "malware" in filename:
            label = +1
        else:
            label = -1

        fn, ext = os.path.splitext(filename)
        fn += "-%s.libsvm" % mode
        utils.save_libsvm(fn, fvecs, label)
