
import re
from collections import Iterable

from lib.adt.tree import Tree
from collections import OrderedDict
from lib.parsing.earley.sentence import Word



class SillyLexer(object):
    
    TEXT = 1
    TOKEN = 2
    
    def __init__(self, token_regexp):
        if not isinstance(token_regexp, str):
            if isinstance(token_regexp, Iterable): token_regexp = "|".join(token_regexp)
            else: raise ValueError("invalid token specification")
        self.token_re = re.compile(token_regexp)
        
    def __call__(self, input_text):
        for (a, val) in self.raw(input_text):
            if a == self.TOKEN: yield val

    def raw(self, input_text):
        pos = 0
        
        for mo in self.token_re.finditer(input_text):
            (from_, to) = mo.span()
            if from_ > pos: yield (self.TEXT, input_text[from_:pos])
            yield (self.TOKEN, self.mktoken(mo))
            pos = to

    def mktoken(self, mo):
        return Word(mo.group(), [mo.lastgroup or mo.group()])



class SillyBlocker(object):
    
    def __init__(self, open_token, close_token):
        self.topen = open_token
        self.tclose = close_token
        
    def __call__(self, token_stream):
        bal = 0
        topen, tclose = self.topen, self.tclose
        bag = []
        for t in token_stream:
            if t == topen:
                bal += 1
            elif t == tclose:
                bal -= 1
            bag += [t]
            if bal == 0: 
                yield Tree(t, list(self(bag[1:-1])))
                bag = []
                
        if bal != 0:
            raise SyntaxError("unbalanced '%s' and '%s'" % (self.topen, self.tclose))


