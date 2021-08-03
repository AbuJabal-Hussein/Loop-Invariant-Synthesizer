#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

from adt.tree import Tree



class ParseTrees:
    def __init__(self, parser):
        '''Initialize a syntax tree parsing process'''
        self.parser = parser
        self.charts = parser.charts
        self.length = len(parser)

        self.nodes = []
        for root in parser.complete_parses:
            self.nodes.extend(self.build_nodes(root))

    def __len__(self):
        '''Trees count'''
        return len(self.nodes)

    def __repr__(self):
        '''String representation of a list of trees with indexes'''
        return '<Parse Trees>\n{0}</Parse Trees>' \
                    .format('\n'.join("Parse tree #{0}:\n{1}\n\n" \
                                        .format(i+1, str(self.nodes[i]))
                                      for i in range(len(self))))

    def build_nodes(self, root):
        '''Recursively create subtree for given parse chart row'''
        # find subtrees of current symbol
        if root.completing:
            down = self.build_nodes(root.completing)
        elif root.dot > 0:
            down = [Tree(root.prev_category())]
        else:
            down = []

        # prepend subtrees of previous symbols
        prev = root.previous
        left = []
        if prev:
            left[:0] = [x.subtrees for x in self.build_nodes(prev)]
            prev = prev.previous
        else:
            left = [[]]

        for x in left: x.extend(down)

        return [Tree(root.rule.lhs, subtrees) for subtrees in left]

