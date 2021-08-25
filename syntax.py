import re

from lib.adt.tree import Tree
from lib.parsing.earley.earley import Grammar, Parser, ParseTrees
from lib.parsing.silly import SillyLexer



class PythonParser(object):

    TOKENS = r"(if|else|elif|while)(?![\w\d_]) (?P<COMMA>\,) (?P<DOT>\.) (?P<LPAREN>\() (?P<NUM>[+\-]?\d+)" \
             r" (?P<ASSOP>[+\-*/]=) (?P<MULTDIV>[*/]) (?P<PLUSMINUS>[+\-])  :" \
             r" (?P<RPAREN>\)) (?P<LSPAREN>\[) (?P<RSPAREN>\]) " \
             r" (?P<NOT>not) (?P<FALSE>False) (?P<TRUE>True) " \
             r" (?P<LEN>len) (?P<INV>__inv__) (?P<REVERSE>reverse) (?P<APPEND>append) (?P<REMOVE>remove) (?P<MAX>max)" \
             r" (?P<INDEX>index) (?P<SUBSTRING>substring) (?P<INT>int)" \
             r" (?P<STR1>\'([^\n\r\"\'\\]|\\[rnt\"\'\\])+\') (?P<STR2>\"([^\n\r\"\'\\]|\\[rnt\"\'\\])+\") " \
             r" (?P<RELOP>[!<>=]=|([<>])) (?P<AND>and) (?P<OR>or) (?P<ID>[^\W\d]\w*) (?P<NEWLINE>[\r\n(\r\n)]+) " \
             r" (?P<INDENT5>(\t\t\t\t\t)) (?P<INDENT4>(\t\t\t\t)) (?P<INDENT3>(\t\t\t)) " \
             r" (?P<INDENT2>(\t\t)) (?P<INDENT>(\t))  =".split()
    GRAMMAR = r"""
    
    S   ->   S1 | S1 NEWLINE | S1 NEWLINE INDENT   |  E  |  S1 NEWLINE S
    
    
    S1  ->   ID = E   | IF_S5 |  IF_S4 | IF_S3 | IF_S2 | IF_S  | WHILE_S5 | WHILE_S4 | WHILE_S3 | WHILE_S2 | WHILE_S  |     ID ASSOP E   |   DEREF = E   |   INV_FUNC | FUNCS
    S1  ->   LPAREN S RPAREN
    
    IF_S -> if E : BLOCK | if E : BLOCK NEWLINE ELSE_S | if E : BLOCK NEWLINE ELIF_S
    IF_S2 -> if E : BLOCK2 | if E : BLOCK2 NEWLINE INDENT ELSE_S2 | if E : BLOCK2 NEWLINE INDENT ELIF_S2 
    IF_S3 -> if E : BLOCK3 | if E : BLOCK3 NEWLINE INDENT2 ELSE_S3 | if E : BLOCK3 NEWLINE INDENT2 ELIF_S3
    IF_S4 -> if E : BLOCK4 | if E : BLOCK4 NEWLINE INDENT3 ELSE_S4 | if E : BLOCK4 NEWLINE INDENT3 ELIF_S4
    IF_S5 -> if E : BLOCK5 | if E : BLOCK5 NEWLINE INDENT4 ELSE_S5 | if E : BLOCK5 NEWLINE INDENT4 ELIF_S5
    
    ELIF_S -> elif E : BLOCK | elif E : BLOCK NEWLINE ELSE_S | elif E : BLOCK NEWLINE ELIF_S
    ELIF_S2 -> elif E : BLOCK2 | elif E : BLOCK2 NEWLINE INDENT ELSE_S2 | elif E : BLOCK2 NEWLINE INDENT ELIF_S2
    ELIF_S3 -> elif E : BLOCK3 | elif E : BLOCK3 NEWLINE INDENT2 ELSE_S3 | elif E : BLOCK3 NEWLINE INDENT2 ELIF_S3
    ELIF_S4 -> elif E : BLOCK4 | elif E : BLOCK4 NEWLINE INDENT3 ELSE_S4 | elif E : BLOCK4 NEWLINE INDENT3 ELIF_S4
    ELIF_S5 -> elif E : BLOCK5 | elif E : BLOCK5 NEWLINE INDENT4 ELSE_S5 | elif E : BLOCK5 NEWLINE INDENT4 ELIF_S5
      
    ELSE_S -> else : BLOCK
    ELSE_S2 -> else : BLOCK2
    ELSE_S3 -> else : BLOCK3
    ELSE_S4 -> else : BLOCK4
    ELSE_S5 -> else : BLOCK5
    
    WHILE_S -> while E : BLOCK
    WHILE_S2 -> while E : BLOCK2
    WHILE_S3 -> while E : BLOCK3
    WHILE_S4 -> while E : BLOCK4
    WHILE_S5 -> while E : BLOCK5
    
    BLOCK ->  NEWLINE INDENT S1 | NEWLINE INDENT S1 BLOCK
    BLOCK2 ->  NEWLINE INDENT2 S1 | NEWLINE INDENT2 S1 BLOCK2
    BLOCK3 ->  NEWLINE INDENT3 S1 | NEWLINE INDENT3 S1 BLOCK3
    BLOCK4 ->  NEWLINE INDENT4 S1 | NEWLINE INDENT4 S1 BLOCK4
    BLOCK5 ->  NEWLINE INDENT5 S1 | NEWLINE INDENT5 S1 BLOCK5

    E   ->   LPAREN E RPAREN | UN_REL E  |    E MULTDIV E   |   E PLUSMINUS E   | E RELOP E | INT LPAREN E RPAREN
    E   ->   E BI_REL E | LIST_E | DEREF | FUNCS
    E   ->   E0
    FUNCS -> LEN_FUNC | REVERSE_FUNC | APPEND_FUNC | REMOVE_FUNC | MAX_FUNC | INDEX_FUNC | SUBSTRING_FUNC
    LEN_FUNC   -> LEN LPAREN E RPAREN
    INV_FUNC   -> INV LPAREN INV_ARGS RPAREN
    REVERSE_FUNC -> REVERSE CALL
    APPEND_FUNC -> APPEND CALL
    REMOVE_FUNC -> REMOVE CALL
    MAX_FUNC -> MAX CALL
    INDEX_FUNC -> INDEX CALL
    SUBSTRING_FUNC -> SUBSTRING MAX
    E0  ->   ID   |   NUM   |   STR   | BOOL
    STR ->   STR1 | STR2
    BOOL -> TRUE | FALSE

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
        program_text = self.preprocess(program_text)
        tokens = list(self.tokenizer(program_text))

        earley = Parser(grammar=self.grammar, sentence=tokens, debug=False)
        earley.parse()
        
        if earley.is_valid_sentence():
            trees = ParseTrees(earley)
            assert(len(trees) == 1)
            return self.postprocess(trees.nodes[0])
        else:
            return None

    def preprocess(self, program_text):
        without_from = re.sub(r'(from)(.*)', r'', program_text)
        # remove comments from the program
        without_comments = re.sub(r'(#)(.*)', r'', without_from)
        # remove tabs in empty lines with only tabs
        return re.sub(r'(\t+)(\n)', r'', without_comments).lstrip()

    def tree_to_list(self, t):
        lst = []
        while len(t.subtrees) != 1:
            lst.append(self.postprocess(t.subtrees[0]))
            t = t.subtrees[2]
        lst.append(self.postprocess(t.subtrees[0]))
        return lst

    def postprocess(self, t, parent_data=None):
        if t.root in ['γ', 'S', 'S1', 'E', 'E0', 'LIST_ITEMS', 'INV_ARGS', 'FUNCS', 'FUNC_ARGS'] and len(t.subtrees) == 1:
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

        elif t.root in ['IF_S', 'IF_S2', 'IF_S3', 'IF_S4', 'IF_S5', 'ELIF_S', 'ELIF_S2', 'ELIF_S3', 'ELIF_S4', 'ELIF_S5']:
            if len(t.subtrees) == 4:
                return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1]), self.postprocess(t.subtrees[3])])
            elif len(t.subtrees) == 6:
                return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1]), self.postprocess(t.subtrees[3]),
                                                 self.postprocess(t.subtrees[5])])
            elif len(t.subtrees) == 7:
                return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1]), self.postprocess(t.subtrees[3]),
                                                 self.postprocess(t.subtrees[6])])
        elif t.root in ['ELSE_S', 'ELSE_S2', 'ELSE_S3', 'ELSE_S4', 'ELSE_S5']:
            return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[2])])

        elif t.root in ['WHILE_S', 'WHILE_S2', 'WHILE_S3', 'WHILE_S4', 'WHILE_S5']:
            return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1]), self.postprocess(t.subtrees[3])])

        elif t.root in ['BLOCK', 'BLOCK2', 'BLOCK3', 'BLOCK4', 'BLOCK5']:
            if len(t.subtrees) == 3:
                return Tree('BLOCK', [self.postprocess(t.subtrees[2])])
            else:
                return Tree('BLOCK', [self.postprocess(t.subtrees[2]), self.postprocess(t.subtrees[3])])

        elif t.root == 'E':
            if len(t.subtrees) == 2:
                return Tree(t.subtrees[0].root, [self.postprocess(t.subtrees[1])])
            elif len(t.subtrees) == 3:
                if t.subtrees[1].root in ['MULTDIV', 'PLUSMINUS', 'RELOP', 'BI_REL']:
                    return Tree(t.subtrees[1].subtrees[0].root, [self.postprocess(t.subtrees[0]), self.postprocess(t.subtrees[2])])
                elif t.subtrees[0].root == 'LPAREN':
                    return self.postprocess(t.subtrees[1])
            elif len(t.subtrees) == 4:
                if t.subtrees[0].root == 'INT':
                    return self.postprocess(t.subtrees[2])

        elif t.root in ['BI_REL', 'UN_REL']:
            return self.postprocess(t.subtrees[0])

        elif t.root == 'INV_FUNC':
            if len(t.subtrees) == 2:
                return Tree(t.subtrees[0].subtrees[0].root, [])
            else:  # len(t.subtrees) == 3
                args = t.subtrees[2]
                lst = [self.postprocess((args.subtrees[0]))]
                lst = lst if len(args.subtrees) == 1 else lst + self.tree_to_list(args.subtrees[2])
                return Tree(t.root, lst)

        elif t.root == 'LEN_FUNC':
            return Tree(t.subtrees[0].subtrees[0].root, [self.postprocess(t.subtrees[2])])

        elif t.root == 'LIST_E':
            if len(t.subtrees) == 2:
                return Tree(t.root, [])
            else:  # len(t.subtrees) == 3
                args = t.subtrees[1]
                lst = [self.postprocess((args.subtrees[0]))]
                lst = lst if len(args.subtrees) == 1 else lst + self.tree_to_list(args.subtrees[2])
                return Tree(t.root, lst)

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

        elif t.root == 'BOOL':
            return Tree(t.root, [Tree(t.subtrees[0].subtrees[0].root == 'True')])

        elif t.root == 'STR':
            return Tree(t.root, [t.subtrees[0].subtrees[0]])

        elif t.root == 'CALL':
            # return  Tree(parent_data, [self.postprocess(t.subtrees[1])])
            if len(t.subtrees) == 2:
                return Tree(parent_data)
            else:  # len(t.subtrees) == 3
                args = t.subtrees[1].subtrees[0]
                lst = [self.postprocess((args.subtrees[0]))]
                lst = lst if len(args.subtrees) == 1 else lst + self.tree_to_list(args.subtrees[2])
                return Tree(parent_data, lst)

        elif t.root in ['REVERSE_FUNC', 'APPEND_FUNC', 'REMOVE_FUNC', 'MAX_FUNC', 'INDEX_FUNC', 'SUBSTRING_FUNC']:
            return self.postprocess(t.subtrees[1], parent_data=t.subtrees[0].subtrees[0].root)

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

    # todo: more list function?

    """
    append - done
    remove
    sort ??
    sum
    find ==> Exists(jj, arr[jj] == 5)
    index ==> IndexOf() - done
    substring ==> IsSubset(a, b)  ,  SubString()
    max ==> use max = If(x > y, x, y) - done
    """

    # ast = PythonParser()("while i < n and n >= 0:\n"
    #                      "\t__inv__(i=i, n=n, x=x, myList=myList)\n"
    #                      "\tx += 1")
    ast = PythonParser()(read_source_file("benchmarks/integers_benchmark/test3_ints.py"))

    if ast:
        print(">> Valid program.")
        print(ast)
    else:
        print(">> Invalid program.")

