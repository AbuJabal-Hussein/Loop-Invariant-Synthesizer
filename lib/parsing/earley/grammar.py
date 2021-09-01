#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys

class Rule:
    def __init__(self, lhs, rhs):
        '''Initializes grammar rule: LHS -> [RHS]'''
        self.lhs = lhs
        self.rhs = rhs

    def __len__(self):
        '''A rule's length is its RHS's length'''
        return len(self.rhs)

    def __repr__(self):
        '''Nice string representation'''
        return "<Rule {0} -> {1}>".format(self.lhs, ' '.join(self.rhs))

    def __getitem__(self, item):
        '''Return a member of the RHS'''
        return self.rhs[item]

    def __eq__(self, other):
        '''Rules are equal iff both their sides are equal'''
        if self.lhs == other.lhs:
            if self.rhs == other.rhs:
                return True
        return False

class Grammar:
    def __init__(self):
        '''A grammar is a collection of rules, sorted by LHS'''
        self.rules = {}
        self.start_symbol = None

    def __repr__(self):
        '''Nice string representation'''
        st = '<Grammar>\n'
        for group in self.rules.values():
            for rule in group:
                st+= '\t{0}\n'.format(str(rule))
        st+= '</Grammar>'
        return st

    def __getitem__(self, lhs):
        '''Return rules for a given LHS'''
        if lhs in self.rules:
            return self.rules[lhs]
        else:
            return None

    def add_rule(self, rule):
        '''Add a rule to the grammar'''
        lhs = rule.lhs
        if lhs in self.rules:
            self.rules[lhs].append(rule)
        else:
            self.rules[lhs] = [rule]

        if self.start_symbol is None: self.start_symbol = lhs

    def remove_rule(self, lhs):
        if lhs in self.rules:
            self.rules.pop(lhs)

    @staticmethod
    def from_file(filename):
        '''Returns a Grammar instance created from a text file.
        '''
        return Grammar.from_lines(open(filename))

    @staticmethod
    def from_string(string):
        '''Returns a Grammar instance created from a string.
        '''
        return Grammar.from_lines(string.splitlines())

    @staticmethod
    def from_lines(iterable):
        '''Returns a Grammar instance created from an iterator over lines.
           The lines should have the format:
               lhs -> outcome | outcome | outcome'''

        grammar = Grammar()
        for line in iterable:
            # ignore comments
            comm = line.find('#')
            if comm >= 0: line = line[:comm]

            line = line.strip()
            if line == '':
                continue

            rule = line.split('->', 1)
            if len(rule) != 2: raise ValueError("invalid grammar format: '%s'" % line)
            lhs = rule[0].strip()
            for outcome in rule[1].split('|'):
                rhs = outcome.strip()
                symbols = rhs.split(' ') if rhs else []
                r = Rule(lhs, symbols)
                grammar.add_rule(r)

        return grammar

