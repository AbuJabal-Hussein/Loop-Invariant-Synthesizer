
from adt.tree import Tree
from parsing.earley.earley import Grammar, Parser, ParseTrees
from parsing.silly import SillyLexer



class PythonParser(object):

    TOKENS = r"(if|else|elif|while)(?![\w\d_]) (?P<COMMA>\,) (?P<DOT>\.) (?P<LPAREN>\() (?P<NUM>[+\-]?\d+)" \
             r" (?P<ASSOP>[+\-*/]=) (?P<MULTDIV>[*/]) (?P<PLUSMINUS>[+\-])  :" \
             r" (?P<RPAREN>\)) (?P<LSPAREN>\[) (?P<RSPAREN>\]) " \
             r" (?P<NOT>not) " \
             r"(?P<LEN>len) (?P<INV>__inv__) (?P<REVERSE>reverse)  (?P<STR1>\'([^\n\r\"\\]|\\[rnt\"\'\\])+\') (?P<STR2>\"([^\n\r\"\\]|\\[rnt\"\'\\])+\") " \
             r" (?P<RELOP>[!<>=]=|([<>])) (?P<AND>and) (?P<OR>or) (?P<ID>[^\W\d]\w*) (?P<NEWLINE>[\r\n(\r\n)]+) (?P<INDENT>(\t)+)  =".split()
    GRAMMAR = r"""
    S   ->   S1 | S1 NEWLINE | S1 NEWLINE INDENT   |   S1 NEWLINE S
    
    S1  ->   ID = E   |   IF_S   |   WHILE_S   |   ID ASSOP E   |   DEREF = E   |   INV_FUNC | FUNCS
    S1  ->   LPAREN S RPAREN
    
    IF_S -> if E : BLOCK NEWLINE ELIF_S | if E : BLOCK NEWLINE ELSE_S | if E : BLOCK
    ELIF_S -> elif E : BLOCK NEWLINE ELIF_S | elif E : BLOCK NEWLINE ELSE_S | elif E : BLOCK
    ELSE_S -> else : BLOCK
    WHILE_S -> while E : BLOCK
    
    BLOCK ->  NEWLINE INDENT S1 | NEWLINE INDENT S1 BLOCK
        
    E   ->   LPAREN E RPAREN | UN_REL E  |    E MULTDIV E   |   E PLUSMINUS E   | E RELOP E
    E   ->   E BI_REL E | LIST_E | DEREF | FUNCS
    E   ->   E0
    FUNCS -> LEN_FUNC | REVERSE_FUNC
    LEN_FUNC   -> LEN LPAREN E RPAREN
    INV_FUNC   -> INV LPAREN INV_ARGS RPAREN
    REVERSE_FUNC     -> REVERSE CALL
    E0  ->   ID   |   NUM   |   STR
    STR ->   STR1 | STR2

    BI_REL -> AND | OR
    UN_REL -> NOT
    CALL   -> LPAREN FUNC_ARGS RPAREN | LPAREN RPAREN
    LIST_E -> LSPAREN LIST_ITEMS RSPAREN | LSPAREN RSPAREN
    LIST_ITEMS -> E | E COMMA LIST_ITEMS
    FUNC_ARGS  -> LIST_ITEMS
    DEREF  -> ID LSPAREN E RSPAREN
    INV_ARGS -> ASSIGN | ASSIGN COMMA INV_ARGS
    ASSIGN -> ID = E
    """
    
    def __init__(self):
        self.tokenizer = SillyLexer(self.TOKENS)
        self.grammar = Grammar.from_string(self.GRAMMAR)

    def __call__(self, program_text):
        tokens = list(self.tokenizer(program_text))

        earley = Parser(grammar=self.grammar, sentence=tokens, debug=False)
        earley.parse()
        
        if earley.is_valid_sentence():
            print(earley)
            trees = ParseTrees(earley)
            print(trees)
            assert(len(trees) == 1)
            return self.postprocess(trees.nodes[0])
        else:
            return None

    def tree_to_list(self, t):
        lst = []
        while len(t.subtrees) != 1:
            lst.append(self.postprocess(t.subtrees[0]))
            t = t.subtrees[2]
        lst.append(self.postprocess(t.subtrees[0]))
        return lst

    def postprocess(self, t):
        if t.root in ['γ', 'S', 'S1', 'E', 'E0', 'LIST_ITEMS', 'INV_ARGS'] and len(t.subtrees) == 1:
            return self.postprocess(t.subtrees[0])
        elif t.root == 'S' and (len(t.subtrees) == 2 or (len(t.subtrees) == 3 and t.subtrees[2].root == 'INDENT')):
            return self.postprocess(t.subtrees[0])
        elif t.root == 'S':  # len(t.subtrees) == 3 and t.subtrees[2].root == 'S'
            return Tree(t.root, [self.postprocess(t.subtrees[0]), self.postprocess(t.subtrees[2])])
        elif t.root == 'S1' and len(t.subtrees) == 3:
            if t.subtrees[1].root == '=':
                return Tree(t.subtrees[1].root, [self.postprocess(t.subtrees[0]), self.postprocess(t.subtrees[2])])
            elif t.subtrees[1].root == 'ASSOP':
                return Tree(t.subtrees[1].subtrees[0].root, [self.postprocess(t.subtrees[0]), self.postprocess(t.subtrees[2])])
            elif t.subtrees[1].root == 'S':
                return self.postprocess(t.subtrees[1])

        elif t.root in ['IF_S', 'ELIF_S']:
            if len(t.subtrees) == 4:
                return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1]), self.postprocess(t.subtrees[3])])
            elif len(t.subtrees) == 6:
                return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1]), self.postprocess(t.subtrees[3]), self.postprocess(t.subtrees[5])])
        elif t.root == 'ELSE_S':
            return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[2])])

        elif t.root == 'WHILE_S':
            return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1]), self.postprocess(t.subtrees[3])])

        elif t.root == 'BLOCK':
            if len(t.subtrees) == 3:
                return Tree(t.root, [self.postprocess(t.subtrees[2])])
            else:
                return Tree(t.root, [self.postprocess(t.subtrees[2]), self.postprocess(t.subtrees[3])])

        elif t.root == 'E':
            if len(t.subtrees) == 2:
                return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1])])
            elif len(t.subtrees) == 3:
                if t.subtrees[1].root in ['MULTDIV', 'PLUSMINUS', 'RELOP', 'BI_REL']:
                    return Tree(t.subtrees[1].subtrees[0].root, [self.postprocess(t.subtrees[0]), self.postprocess(t.subtrees[2])])
                elif t.subtrees[0].root == 'LPAREN':
                    return self.postprocess(t.subtrees[1])

        elif t.root in ['BI_REL', 'UN_REL']:
            return self.postprocess(t.subtrees[0])

        elif t.root == 'INV_FUNC':
            if len(t.subtrees) == 2:
                return Tree(t.subtrees[0].subtrees[0].root, [])
            else:  # len(t.subtrees) == 3
                args = t.subtrees[2]
                lst = [self.postprocess((args.subtrees[0]))]
                return Tree(t.root, lst + self.tree_to_list(args.subtrees[2]))

        elif t.root == 'LEN_FUNC':
            return Tree(t.subtrees[0].subtrees[0].root, [self.postprocess(t.subtrees[2])])

        elif t.root == 'LIST_E':
            if len(t.subtrees) == 2:
                return Tree(t.root, [])
            else:  # len(t.subtrees) == 3
                args = t.subtrees[1]
                lst = [self.postprocess((args.subtrees[0]))]
                return Tree(t.root, lst + self.tree_to_list(args.subtrees[2]))

        # elif t.root in ['LIST_ITEMS', 'INV_ARGS']:  # it should be guaranteed that len(t.subtrees) == 3
        #     lst = [self.postprocess((t.subtrees[0]))]
        #     print('+++++++')
        #     print(t.subtrees[0])
        #     print(t.subtrees[0].root)
        #     return Tree(t.subtrees[0].root, lst + self.tree_to_list(t.subtrees[2]))

        elif t.root == 'DEREF':
            return Tree(t.root, [self.postprocess(t.subtrees[0]), self.postprocess(t.subtrees[2])])

        elif t.root == 'ASSIGN':
            return Tree(t.subtrees[1].root, [self.postprocess(t.subtrees[0]), self.postprocess(t.subtrees[2])])

        elif t.root == 'NUM':
            return Tree(t.root, [Tree(int(t.subtrees[0].root))])  # parse ints

        return Tree(t.root, [self.postprocess(s) for s in t.subtrees])
    

def read_source_file(path):
    src_file = open(path, "r")
    src = src_file.read()
    src_file.close()
    # print(src)
    return src



if __name__ == '__main__':
    """
    ast = PythonParser()("if 1 : \n"
                         "\t c = 2\n"
                         "\t a = 3\n"
                         "elif q == r:\n"
                         "\t c = 1\n"
                         "\t a = 2\n"
                         "elif q > p:\n"
                         "\t c = 65\n"
                         "else:\n"
                         "\t a = 213\n"
                         "t = r\n"
                         )
    """
    """
    ast = PythonParser()("a = 7\n\n\n"
                         "while not 0:\n"
                         "\t if a > 2:\n"
                         "\t\t if b > 0:\n"
                         "\t\t\t l = 5\n"
                         "\t\t a -= 1\n"
                         "b *= 4")
    """

    """
    ast = PythonParser()("a = 7\n\n\n"
                         "while a > 2:\n"
                         "\t a = 8\n"
                         "\t b /= 2\n"
                         "\t if a == b:\n"
                         "\t\t a *= 2\n"
                         "\t b -= 3\n"
                         "b *= 4\n")
    """

    """
    ast = PythonParser()(
                         "lst = [4, 5,w,[],[5,9]]\n"
                         "lst[4] = lst[p]\n"
                         "n = len(lst) + 7\n"
                         "o *= 8-1 / 7\n"
                         "x = a > 0 and (b < 3)\n"
                         "__inv__(i=i , x=x , n=n)\n"
                         )
    """
    # todo: x = a > 0 and b < 3  is being interpreted as x = ((a > 0) and b) < 3 but it should be x = (a > 0) and (b < 3)
    # todo: fix issue: signed numbers does not work     - fixed
    # todo: add String support                          - fixed
    # todo: more list function?

    # ast = PythonParser()("while i < n and n >= 0:\n"
    #                      "\t__inv__(i=i, n=n, x=x, myList=myList)\n"
    #                      "\tx += 1")
    ast = PythonParser()(read_source_file("benchmarks/b1.py"))

    if ast:
        print(">> Valid program.")
        print(ast)
    else:
        print(">> Invalid program.")

