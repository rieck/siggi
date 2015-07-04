#!/usr/bin/env python
# Shorty - Shortest-Path Graph Embedding
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import utils
import sys
import os

for arg in sys.argv[1:]:
    base, ext = os.path.splitext(arg)

    if ext != ".zip":
        continue
        
    if base.endswith("-dot"):
        continue

    print "Loading FCG graphs from %s" % arg
    graphs = utils.load_fcg_zip(arg)
    
    print "Saving DOT graphs to %s-dot%s" % (base,ext)
    utils.save_dot_zip(graphs, "%s-dot%s" % (base,ext))
