#!/usr/bin/env python
# Siggie - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import unittest

import networkx as nx
import pygraphviz as pg

import siggie

# Test cases in DOT format
dot_strings = [
    # Empty graph
    """ digraph {
    } """,

    # Disconnected graph
    """ digraph {
        1 [label="A"]; 2 [label="A"]; 3 [label="B"];
    } """,

    # Chain graph
    """ digraph {
        1 [label="A"]; 2 [label="B"]; 3 [label="A"];
        1 -> 2 -> 3; 3 -> 2 -> 1
    } """,

    # Graph from README
    """ digraph {
        1 [label="A"]; 2 [label="B"]; 3 [label="C"]; 4 [label="A"];
        5 [label="B"]; 6 [label="C"];
        1 -> 2 -> 3 -> 4 -> 5 -> 6; 5 -> 2;
    } """,

    # Attracting loops
    """ digraph {
        1 [label="A"]; 2 [label="B"]; 3 [label="C"];
        4 [label="A"]; 5 [label="B"]; 6 [label="C"];
        1 -> 2 -> 3 -> 1 ; 4 -> 5 -> 6 -> 4;
        2 -> 4; 4 -> 2;
    } """
]


def get_graph(string):
    """ Create a graph from a DOT string """
    dot = pg.AGraph(string)
    return nx.from_agraph(dot)


class TestCases(unittest.TestCase):
    def test_bag_of_nodes(self):
        """ Test bag of nodes """
        bags = [
            {},  # Empty graph
            {"A": 2, "B": 1},  # Disconnected graph
            {"A": 2, "B": 1},  # Chain graph
            {"A": 2, "B": 2, "C": 2},  # Graph from README
            {"A": 2, "B": 2, "C": 2},  # Attracting loops
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggie.bag_of_nodes(graph)
            self.assertEqual(bag, bags[i])

    def test_bag_of_edges(self):
        """ Test bag of edges """
        bags = [
            {},  # Empty graph
            {},  # Disconnected graph
            {"A-B": 2, "B-A": 2},  # Chain graph
            {"A-B": 2, "B-B": 1, "B-C": 2, "C-A": 1},  # Graph from README
            {"A-B": 3, "B-C": 2, "C-A": 2, "B-A": 1},  # Attracting loops
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggie.bag_of_edges(graph)
            self.assertEqual(bag, bags[i])


if __name__ == '__main__':
    unittest.main()
