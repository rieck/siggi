#!/usr/bin/env python
# Siggi - Feature Hashing for Labeled Graphs
# (c) 2015 Konrad Rieck (konrad@mlsec.org)

import unittest

import networkx as nx
import pygraphviz as pg

import siggi

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
        1 -> 2 -> 3; 3 -> 2 -> 1;
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
        2 -> 4;
    } """
]


def get_graph(string):
    """ Create a graph from a DOT string """
    dot = pg.AGraph(string)
    return nx.from_agraph(dot)


class TestCases(unittest.TestCase):
    def test_bag_of_nodes(self):
        bags = [
            {},  # Empty graph
            {"A": 2, "B": 1},  # Disconnected graph
            {"A": 2, "B": 1},  # Chain graph
            {"A": 2, "B": 2, "C": 2},  # Graph from README
            {"A": 2, "B": 2, "C": 2},  # Attracting loops
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_nodes(graph)
            self.assertEqual(bag, bags[i])

    def test_bag_of_edges(self):
        bags = [
            {},  # Empty graph
            {},  # Disconnected graph
            {"A-B": 2, "B-A": 2},  # Chain graph
            {"A-B": 2, "B-B": 1, "B-C": 2, "C-A": 1},  # Graph from README
            {"A-B": 2, "B-C": 2, "C-A": 2, "B-A": 1},  # Attracting loops
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_edges(graph)
            self.assertEqual(bag, bags[i])

    def test_bag_of_neighborhoods(self):
        bags = [
            {},  # Empty graph
            {"A:": 2, "B:": 1},  # Disconnected graph
            {"A:A-B": 2, "B:A-A": 1},  # Chain graph
            # Graph from README
            {
                "A:B-B-C": 1, "A:B-C": 1, "B:A-C": 1, "B:B-C-C": 1,
                "C:": 1, "C:A-B": 1
            },
            # Attracting loops
            {
                "A:A-B-C": 1, "B:A-A-B-C": 1, "C:A-B": 2, "B:A-C": 1,
                "A:B-C": 1,
            },
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_neighborhoods(graph, size=2)
            self.assertEqual(bag, bags[i])

    def test_bag_of_reachabilities(self):
        bags = [
            {},  # Empty graph
            {},  # Disconnected graph
            {"A:B": 2, "A:A": 2, "B:A": 2},  # Chain graph
            # Graph from README
            {
                "A:B": 3, "A:C": 2, "B:A": 1, "B:B": 1, "B:C": 3,
                "C:A": 1, "C:B": 1
            },
            # Attracting loops
            {
                "A:B": 2, "A:A": 1, "A:C": 2, "B:A": 3, "B:B": 1,
                "B:C": 2, "C:A": 2, "C:B": 2
            },
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_reachabilities(graph, depth=2)
            self.assertEqual(bag, bags[i])

    def test_bag_of_shortest_paths(self):
        bags = [
            {},  # Empty graph
            {},  # Disconnected graph
            {"A-B-A": 2},  # Chain graph
            # Graph from README
            {
                "B-C-A-B": 1, "B-C-A": 1, "B-B-C-A": 1, "B-B-C": 1,
                "A-B-C-A": 1, "C-A-B-B": 1, "C-A-B-C": 1, "C-A-B": 1,
                "A-B-B": 1, "A-B-C": 2, "A-B-B-C": 1
            },
            # Attracting loops
            {
                "A-B-A-B": 1, "B-A-B": 1, "B-A-B-C": 1, "B-C-A": 2,
                "C-A-B-A": 1, "C-A-B": 2, "A-B-C": 2, "A-B-A": 1
            },
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_shortest_paths(graph, minlen=2, maxlen=3)
            self.assertEqual(bag, bags[i])

    def test_bag_of_connected_components(self):
        bags = [
            {},  # Empty graph
            {"A": 2, "B": 1},  # Disconnected graph
            {"A-A-B": 1},  # Chain graph
            {"A": 1, "A-B-B-C": 1, "C": 1},  # Graph from README
            {"A-B-C": 2},  # Attracting loops
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_connected_components(graph)
            self.assertEqual(bag, bags[i])

    def test_bag_of_attracting_components(self):
        bags = [
            {},  # Empty graph
            {"A": 2, "B": 1},  # Disconnected graph
            {"A-A-B": 1},  # Chain graph
            {"C": 1},  # Graph from README
            {"A-B-C": 1},  # Attracting loops
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_attracting_components(graph)
            self.assertEqual(bag, bags[i])

    def test_of_elementary_cycles(self):
        bags = [
            {},  # Empty graph
            {},  # Disconnected graph
            {"A-B": 2},  # Chain graph
            {"A-B-B-C": 1},  # Graph from README
            {"A-B-C": 2},  # Attracting loops
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_elementary_cycles(graph)
            self.assertEqual(bag, bags[i])

    def test_of_branchless_paths(self):
        bags = [
            {},  # Empty graph
            {"A": 2, "B": 1},  # Disconnected graph
            {"A": 2},  # Chain graph
            {"A-B-C-A": 1, "C": 1},
            {"C-A-B": 1, "C-A": 1},
        ]

        for i, string in enumerate(dot_strings):
            graph = get_graph(string)
            bag = siggi.bag_of_branchless_paths(graph)
            self.assertEqual(bag, bags[i])


if __name__ == "__main__":
    unittest.main()
