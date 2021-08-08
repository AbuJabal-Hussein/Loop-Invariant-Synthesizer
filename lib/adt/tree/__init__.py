
class Tree(object):
    
    def __init__(self, root, subtrees=None):
        self.root = root
        if subtrees is None:
            self.subtrees = []
        else:
            self.subtrees = subtrees
        
    def __eq__(self, other):
        if not isinstance(other, Tree): return NotImplemented
        return type(self) == type(other) and \
               (self.root, self.subtrees) == (other.root, other.subtrees)    
    
    def __ne__(self, other):
        return not (self == other)
    
    def __hash__(self):
        return hash((self.root, tuple(self.subtrees)))
    
    def repr(self, leaf_fmt):
        if self.subtrees:
            subreprs = ", ".join(x.repr(leaf_fmt) for x in self.subtrees)
            return "%s{%s}" % (leaf_fmt(self.root), subreprs)
        else:
            return leaf_fmt(self.root)
    
    def __repr__(self):  return self.repr(repr)
    def __str__(self):   return self.repr(str)
    
    def clone(self):
        return self.reconstruct(self)
    
    @classmethod
    def reconstruct(cls, t):
        return cls(t.root, [cls.reconstruct(s) for s in t.subtrees])
        
    @property
    def nodes(self):
        return list(PreorderWalk(self))
    
    @property
    def leaves(self):
        return [n for n in PreorderWalk(self) if not n.subtrees]

    @property
    def before_leaves(self):
        return [n for n in PreorderWalk(self) if n.subtrees and not n.subtrees[0].subtrees]
    
    @property
    def terminals(self):
        """ @return a list of the values located at the leaf nodes. """
        return [n.root for n in self.leaves]

    @property
    def depth(self):
        """ Computes length of longest branch (iterative version). """
        stack = [(0, self)]
        max_depth = 0
        while stack:
            depth, top = stack[0]
            max_depth = max(depth, max_depth)
            stack[:1] = [(depth+1,x) for x in top.subtrees]
        return max_depth

    def split(self, separator=None):
        if separator is None: separator = self.root
        if self.root == separator: return [item for s in self.subtrees for item in s.split(separator)]
        else: return [self]

    def fold(self):
        return type(self)(self.root, self.split())


# @deprecated: clients should use adt.tree.walk.RichTreeWalk instead
from .walk import PreorderWalk, RichTreeWalk as Walk
Visitor = Walk.Visitor

