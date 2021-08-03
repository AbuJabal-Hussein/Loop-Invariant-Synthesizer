from z3 import *


class BottomUp:

    def __init__(self, grammar, tokens, prog_states_file, solver=None):
        '''
        Initialised with grammar and its tokens
        :param grammar: The Grammar. non-terminals on the right-hand side of production rules are delimited by spaces
         from other tokens in the same rule. Furthermore, non-terminals are identifiers written in ALL CAPS.
        :param tokens: The Grammar's tokens
        '''

        self.grammar = grammar
        self.tokens = tokens
        self.p = list()
        self.program_states_file = prog_states_file
        self.program_states = list()
        self.arrays_dict = {}  # {Array_name -> {index -> (arr_name, index)} }
        self.parse_prog_states()

    def extract_non_terminals(self):
        pass

    def grow(self):
        current_form = self.p.pop
        batch = list()
        # TODO: self.p.add()
        return batch

    def elimEquivalents(self, batch):
        """
        Affects self.p
        :return:
        """
        s = Solver()
        for i, x in enumerate(batch):
            for y in batch[i+1:]:
                s.add(Not(x == y))
                if s.check() == unsat:  # proved to be equal
                    batch.remove(y)
                s.reset()
        return batch



    def get_parsed_states(self):
        return self.program_states

    def parse_prog_states(self):
        import ast
        if self.program_states is None or len(self.program_states) > 0:
            self.program_states = list()

        def assert_array(array_name, data):
            arr2str_name = "%s__str" % array_name
            arr2int_name = "%s__int" % array_name
            array_str = Array(arr2str_name, IntSort(), StringSort())
            array_int = Array(arr2int_name, IntSort(), IntSort())
            pos_converter = {}
            i_str = i_int = 0
            constrains = []
            for i, d in enumerate(data):
                if type(d) is int:
                    tmp = Int(arr2int_name + str(i_int))
                    constrains.append(And(tmp == d, array_int[i_int] == tmp))
                    pos_converter[i] = (arr2int_name, i_int)
                    i_int += 1

                if type(d) is str:
                    strval = StringVal(d)
                    tmp = String(arr2str_name + str(i_str))
                    constrains.append(And(tmp == strval,
                                          array_str[i_str] == tmp))
                    pos_converter[i] = (arr2str_name, i_str)
                    i_str += 1
            self.arrays_dict[array_name] = pos_converter
            return constrains

        def to_z3type(v, t, val):
            if t == "int":
                return Int(v), int(val)
            if t == "str":
                return String(v), val

        with open(self.program_states_file, "r") as source:
            content = source.read()
            for line in content.split(sep='\n'):
                if not line:
                    continue
                curr_state_rules = list()
                for var_data in line.split(sep='\x1F'):
                    var, t, value = var_data.split(sep=' ', maxsplit=2)
                    if t == 'list':
                        curr_state_rules = curr_state_rules + assert_array(var, ast.literal_eval(value))
                    else:
                        z3type, z3value = to_z3type(var, t, value)
                        curr_state_rules.append(z3type == z3value)
                self.program_states.append(curr_state_rules)

    def bottom_up(self, terminals, non_term, rules, starting, program_states):
        self.p = list()  # Should be a list of formulas, terminal OP token/terminal, or the opposite.

        while True:
            curr_batch = self.grow()
            curr_batch = self.elimEquivalents(
                curr_batch)  # probably using z3, since I want to find similar invariants(formulas) not programs
            for inv in curr_batch:
                for state in self.program_states:
                    s = Solver()
                    s.add(state)
                    if s.check() == sat:
                        # TODO: it yields if one state is good. need to check on each and yield if all
                        yield inv
            self.p = self.p + curr_batch


s = Solver()
I = Int("i")
s.add(And(I >= 0, I < 4))
TOKENS = r"(if|then|else|while|do|skip)(?![\w\d_])   (?P<id>[^\W\d]\w*)   (?P<num>[+\-]?\d+)   (?P<op>[!<>]=|([+\-*/<>=]))    [();]  :=".split()
GRAMMAR = r"""
S   ->   S1     |   S1 ; S
S1  ->   skip   |   id := E   |   if E then S else S1   |   while E do S1
S1  ->   ( S )
E   ->   E0   |   E0 op E0
E0  ->   id   |   num
E0  ->   ( E )
"""
bt = BottomUp(grammar=GRAMMAR, tokens=TOKENS, prog_states_file="programStates.txt")
for state in bt.get_parsed_states():
    s.add(state)
    print("---------------------------------------------------------------------")
    print(s)
    print(s.check())
    print(s.model())
    s.reset()
    s.add(And(I >= 0, I < 4))
    print("---------------------------------------------------------------------")
