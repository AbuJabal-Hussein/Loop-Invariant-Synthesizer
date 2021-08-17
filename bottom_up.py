from z3 import *

from adt.tree import Tree
from lib.parsing.earley.earley import Grammar
from lib.adt.tree.walk import PreorderWalk
from lib.parsing.silly import SillyLexer, Word
import itertools
from copy import deepcopy
from VC_Generation import *
import multiprocessing
from time import time



def check_passing(generator, ast_chunks, x_):  # TODO: Rename
    res = []
    s_ = Solver()
    x_ast = generator.parser(x_)
    x = generator.generate_vc(x_ast)[0]
    for y_ in ast_chunks:
        s_.reset()
        ast = generator.parser(y_)
        y = generator.generate_vc(ast)[0]
        s_.add(Not(x == y))
        if s_.check() == unsat:  # proved to be equal
            continue
        res.append(y_)

    return res


def remove_equal(x, ys, z3_to_str):
    """

    :param x: what to compare to
    :param ys: List[(index, z3 object)]
    :return:
    """
    adder = []
    for i, y in ys:
        s_ = Solver()
        s_.add(Not(x == y))
        if s_.check() == unsat:  # proved to be equal
            continue
        adder.append(z3_to_str[y])
    # print(multiprocessing.current_process().ident)
    return adder


class BottomUp:

    def __init__(self, grammar, tokens, prog_file, prog_states_file):
        """
        Initialised with grammar and its tokens
        :param grammar: The Grammar. non-terminals on the right-hand side of production rules are delimited by spaces
         from other tokens in the same rule. Furthermore, non-terminals are identifiers written in ALL CAPS.
        :param tokens: The Grammar's tokens
        """
        self.rev_dict = dict()
        self.strings = []
        self.grammar = Grammar.from_string(grammar)
        self.tokenizer = SillyLexer(tokens)
        print(self.grammar)
        if not self.grammar or "VAR" not in self.grammar.rules:
            raise Exception("Grammar or Rule With 'VAR' in LHS missing")
        self.tokens = self.extract_tokens(prog_file)  # Used tokens in the python code
        # Dictionary: 'num': {'1', '3'}, 'op': {'+', '=', '<', '>='}, where 1, 3 and the ops are the used tokens in code
        self.used_tokens_dict = self.build_tokens_dict()
        # Similar dictionary to the one above but for all starting and grown ones
        self.reverse_dict = {"id": [],
                             "num": [],
                             "op": []}
        self.p = [rule.rhs[0] for rule in self.grammar["VAR"]]
        self.program_states_file = prog_states_file  # Where __inv__ prints
        self.program_states = list()  #
        self.arrays_dict = {}  # {Array_name -> {index -> (arr_name, index)} }
        self.vars_dict = dict()
        self.vars_dict_multi = dict()
        self.tagged_vars = dict()
        self.parse_prog_states()
        self.vc_gen = VCGenerator(self.vars_dict, should_tag=False)
        self.z3_to_str = dict()

    def extract_tokens(self, prog_file):
        tokens = set()
        with open(prog_file, "r") as source:
            content = source.read()
            for line in content.split(sep='\n'):
                tokens.update(set(self.tokenizer(line)))
        return tokens

    def build_tokens_dict(self):
        def f(d_: Word):
            return d_.tags[0], d_.word
        dictionary = dict()
        for token in self.tokens:
            a, b = f(token)
            dictionary.setdefault(a, set()).add(b)
        return dictionary

    def extract_non_terminals(self):
        pass

    def grow(self):
        def f(tup, index, var):
            """
            inserts var in index index in tup, returns all as str
            """
            as_list = list(tup)
            return "".join(as_list[:index]) + var + "".join(as_list[index:])
        batch = list()
        local_rev_dic = deepcopy(self.reverse_dict)
        # print("In Grow:")
        # print("    self.reverse_dict: {}".format(self.reverse_dict))
        # print("    self.rev_dict: {}".format(self.rev_dict))
        # print("    self.p: {}".format(self.p))
        for key in self.reverse_dict.keys():
            local_rev_dic[key].extend(self.rev_dict.setdefault(key, []))
        for key in self.used_tokens_dict.keys():
            if key not in local_rev_dic:
                local_rev_dic[key] = self.used_tokens_dict[key].copy()
        local_p = set(self.p.copy())
        for current_form in local_p:
            tags = current_form.tags.copy()
            for tag in tags:
                for l in self.grammar.rules.values():
                    for rule in l:
                        lhs, symbols = rule.lhs, rule.rhs
                        if len(rule.rhs) == 1 and rule.rhs[0] == tag:
                                new_form = Word(current_form.word, [lhs])
                                batch.append(new_form)
                                self.reverse_dict.setdefault(lhs, []).append(new_form.word)
                                continue
                        for i, symbol in enumerate(rule.rhs):
                            if symbol == tag:
                                ts = rule.rhs[:i] + rule.rhs[i+1:]
                                if any(t not in local_rev_dic for t in ts):
                                    continue
                                tmp = [list(local_rev_dic[t]) for t in ts]
                                tuples = list(itertools.product(*tmp))  # NEEDS FIX, debug and check value
                                for tupl in tuples:
                                    new_form = Word(f(tupl, i, current_form.word), [lhs])
                                    batch.append(new_form)
                                    self.reverse_dict.setdefault(lhs, []).append(new_form.word)

                if current_form.word in self.reverse_dict[tag]:
                    self.reverse_dict[tag].remove(current_form.word)
                local_rev_dic[tag].remove(current_form.word)
            self.p.remove(current_form)

        #           Remove current_form.word from self.reverse_dict[tag]
        #           making sure that there was no rules as E -> E is not needed
        return batch

    @staticmethod
    def elim_equivalents(batch):
        """
        Affects self.p
        :return:
        """
        s_ = Solver()
        for i, x in enumerate(batch):
            to_remove = []
            for j in range(i+1, len(batch)):
                y = batch[j]
            # for y in batch[i+1:]:
                s_.add(Not(x == y))
                if s_.check() == unsat:  # proved to be equal
                    to_remove.append(y)
                s_.reset()
            for r in to_remove:
                batch.remove(r)
            print("Finished %d" % i)
        return batch

    @staticmethod
    def elim_equivalents_multi_proccess(batch: list, generator, vars_dict):
        started = time()
        total_size = len(batch)
        def chunkIt(seq, split):
            avg = len(seq) / float(split)
            out = []
            last = 0.0

            while last < len(seq):
                out.append(seq[int(last):int(last + avg)])
                last += avg

            return out

        with open("timers.txt", "a") as profiler:
            profiler.write("\n\n------------------Starting new Elim-------------------------\n")
            ready = []
            num = min(multiprocessing.cpu_count() - 1, 8)
            print("num CPUS: %d" % num)
            while len(batch) > 1:
                start_while = time()
                # x = deepcopy(batch[0]).translate(ctx)
                pool = multiprocessing.Pool(processes=num)
                # processes = []
                # should_remove = dict()
                # for j in range(1, len(batch)):
                #     y = batch[j]
                #     should_remove[j] = pool.apply_async(remove_equal, [x, y, lambda d_: batched.append(d_)]).get()
                chunks = chunkIt(batch, num)
                x = batch[0]
                async_results = []
                for chunk in chunks:
                    # proc = multiprocessing.Process(target=remove_equal, args=[x, chunk, lambda d_: batched.append(d_)])
                    # proc.start()
                    # processes.append(proc)
                    # res = pool.apply_async(remove_equal, [x, chunk, z3_to_str])
                    res = pool.apply_async(check_passing, [VCGenerator(vars_noz3=vars_dict, should_tag=False), chunk, x])
                    async_results.append(res)

                pool.close()
                pool.join()
                x_ast = generator.parser(x)
                # print(x)
                ready.append(generator.generate_vc(x_ast)[0])
                batched = []
                for async_res in async_results:
                    results = async_res.get()
                    for res in results:
                        batched.append(res)

                pool = multiprocessing.Pool(num)
                # for proc in processes:
                #     proc.join()
                batch = batched
                print("Finished %d" % len(ready))
                now = time()
                profiler.write("{} started at: {} ended at {}  Total: {}\n".format(len(ready), start_while, now,
                                                                                 now-start_while))

            if len(batch) == 1:
                b = generator.parser(batch[0])
                ready.append(generator.generate_vc(b)[0])
            now = time()
            profiler.write("\n\neliminate finished at: {}  Total time: {}\n".format(now, now - started))

        return ready

    def check_sat(self, inv):
        for state in self.program_states:
            s_ = Solver()
            s_.add(state)
            s_.add(inv)
            if s_.check() == unsat:
                return False
        return True

    def get_parsed_states(self):
        return self.program_states

    def parse_prog_states(self):
        import ast
        if self.program_states is None or len(self.program_states) > 0:
            self.program_states = list()

        def assert_array(array_name, ds):
            arr2str_name = "%s__str" % array_name
            arr2int_name = "%s__int" % array_name
            array_str = Array(arr2str_name, IntSort(), StringSort())
            array_int = Array(arr2int_name, IntSort(), IntSort())
            pos_converter = {}
            i_str = i_int = 0
            constrains = []
            for i, data in enumerate(ds):
                if type(data) is int:
                    tmp = Int(arr2int_name + str(i_int))
                    constrains.append(And(tmp == data, array_int[i_int] == tmp))
                    pos_converter[i] = (arr2int_name, i_int)
                    i_int += 1

                if type(data) is str:
                    strval = StringVal(data)
                    tmp = String(arr2str_name + str(i_str))
                    constrains.append(And(tmp == strval,
                                          array_str[i_str] == tmp))
                    pos_converter[i] = (arr2str_name, i_str)
                    i_str += 1
            self.arrays_dict[array_name] = pos_converter
            if i_int > i_str:
                return constrains, IntSort(), array_int
            return constrains, StringSort(), array_str

        def arr_to_z3_1type(array_name, ds):
            constrains = []
            arr_z3sort = None
            if type(ds[0]) is int:
                arr_z3sort = IntSort()
                arr = Array(array_name, IntSort(), arr_z3sort)
                for i, data in enumerate(ds):
                    constrains.append(arr[i] == data)
            else:
                arr_z3sort = StringSort()
                arr = Array(array_name, IntSort(), arr_z3sort)
                for i, data in enumerate(ds):
                    strval = StringVal(data)
                    constrains.append(arr[i] == strval)

            return constrains, arr_z3sort, arr

        def to_z3type(v_, t_, val):
            if t_ == "int":
                return Int(v_), int(val), IntSort(), Int
            if t_ == "str":
                return String(v_), val, StringSort(), String

        with open(self.program_states_file, "r") as source:
            content = source.read()
            for line in content.split(sep='\n'):
                if not line:
                    continue
                curr_state_rules = list()
                for var_data in line.split(sep='\x1F'):
                    var, t, value = var_data.split(sep=' ', maxsplit=2)
                    if t == 'list':
                        data = ast.literal_eval(value)
                        cons, z3sort, z3type = arr_to_z3_1type(var, data)
                        curr_state_rules = curr_state_rules + cons
                        self.vars_dict[var] = [z3type, z3sort, len(data)]
                        self.vars_dict_multi[var] = ["array", True, len(data)]
                    else:

                        z3type, z3value, z3sort, builder = to_z3type(var, t, value)
                        curr_state_rules.append(z3type == z3value)
                        self.vars_dict[var] = [z3type, z3sort, 1]
                        self.vars_dict_multi[var] = [builder, True, 1]
                self.program_states.append(curr_state_rules)

    def build_starting_p(self):
        """
        Builds starting p and the transposed dictionary
        :return:
        """
        p = []
        for _type in self.reverse_dict.keys():
            if _type == "id":
                for var in self.used_tokens_dict[_type].intersection(self.p):
                    p.append(Word(var, ['id']))
                    self.reverse_dict[_type].append(var)
                continue

            if _type in self.used_tokens_dict:
                for var in self.used_tokens_dict[_type]:
                    p.append(Word(var, [_type]))
                    self.reverse_dict[_type].append(var)
        return p

    def tag_and_convert(self, inv):
        inv_str = self.z3_to_str[inv]
        ast = deepcopy(self.vc_gen.parser(inv_str))
        adding = dict()
        for node in PreorderWalk(ast):
            if node.root == 'ID':
                var = node.subtrees[0].root
                if var in self.vars_dict:
                    lst = self.vars_dict[var]
                    if lst[2] > 1 or var.endswith("_"):  # A list
                        continue
                    tagged = var + "_"
                    node.subtrees[0] = Tree(tagged)
                    if tagged not in self.vars_dict.keys():
                        adding[tagged] = [Int(tagged) if self.vars_dict[var][0].is_int()
                                          else String(tagged), lst[1], lst[2]]
        for k, elem in adding.items():
            self.vars_dict[k] = elem
            self.tagged_vars[k] = elem
        return self.vc_gen.generate_vc(ast)[0]

    def batch_to_z3(self, batch):
        self.strings = []
        lst = []
        print("in converting, self.vars_dict {}".format(self.vars_dict))
        for code in batch:
            if type(code) is not str:
                word = code.word
            else:
                word = code
            inv = None
            ast = self.vc_gen.parser(word)
            if ast is None or ast.depth < 2:
                continue
            try:
                inv = self.vc_gen.generate_vc(ast)[0]
            except TypeError as err:
                if "not supported between instances of " in err.args[0] \
                        or "unsupported operand type(s) for" in err.args[0]:
                    continue
                else:
                    raise err
            except z3.z3types.Z3Exception as err:
                if 'sort mismatch' in err.args[0]:
                    continue
                raise err
            except KeyError as kerr:
                continue
            if type(inv) is bool or (type(inv) == BoolRef and (inv == True or inv == False)):
                continue
            t = simplify(inv)
            print("str: {} ast: {} Inv: {} simplified: {}".format(word, ast, inv, t))
            if type(t) == BoolRef and (t == True or t == False):  # simply equal to True (e.g. y<=y)
                continue
            self.z3_to_str[inv] = word
            lst.append(inv)
            self.strings.append(word)
            # lst.append(self.vc_gen.generate_vc(ast))
        return lst

    # def inv_tagged(self, inv):
    #     inv_str = self.z3_to_str[inv]
    #     adding = dict()
    #     for var, l in self.vars_dict.items():
    #         if l[2] > 1 or var.endswith("_"):  # A list
    #             continue
    #         tagged = var + "_"
    #         if var in inv_str and tagged not in self.vars_dict.keys():
    #             adding[tagged] = [Int(tagged) if self.vars_dict[var][0].is_int() else String(tagged), l[1], l[2]]
    #         inv_str = inv_str.replace(var, tagged)
    #     for k, elem in adding.items():
    #         self.vars_dict[k] = elem
    #     self.tagged_vars = adding
    #     return inv_str

    def bottom_up(self):
        # print("HMMM")
        self.p = self.build_starting_p()
        # print("before Grow:")
        # print(self.p)
        # print("self.reverse_dict:")
        # print(self.reverse_dict)
        starting = deepcopy(self.p)
        self.rev_dict = deepcopy(self.reverse_dict)
        # ehhs = dict()
        i = 0
        # ehh = 0
        while True:
            i = i + 1
            self.z3_to_str = dict()
            curr_batch = self.grow()
            # print("grow:")
            # print(curr_batch)
            # print("self.reverse_dict:")
            # print(self.reverse_dict)
            print("-------------------%d-----------------" % i)
            print("Batch size: %d" % len(curr_batch))
            # z3_batch = list(self.vc_gen.generate_vc(self.vc_gen.parser(b.word)) for b in curr_batch)
            z3_batch = self.batch_to_z3(curr_batch)
            print("converted %d:" % len(z3_batch))
            print(z3_batch)
            z3_batch = self.elim_equivalents_multi_proccess(self.strings, self.vc_gen, self.vars_dict_multi)
            print("Eliminated\nNew Size: %d" % len(z3_batch))
            sats = []
            for inv in z3_batch:
                if self.check_sat(inv):
                    inv_tagged = self.tag_and_convert(inv)
                    # inv_tagged = self.batch_to_z3([self.inv_tagged(inv)])[0]
                    print("Inv {} and Tagged {}".format(inv, inv_tagged))
                    sats.append((inv, inv_tagged))
            for tagged in self.tagged_vars:
                del self.vars_dict[tagged]
            print("after delete of self.vars_dict {}\n self.tagged_vars: {}".format(self.vars_dict, self.tagged_vars))
            self.tagged_vars.clear()
            yield sats
            print("Yielded")
            # ehhs[ehh] = curr_batch.copy()
            # ehh = ehh + 1
            # if len(ehhs.keys()) > 7:
            #     yield curr_batch
            for word in curr_batch:
                if word.word in self.z3_to_str.values():
                    self.p.append(word)
            self.p.extend(deepcopy(starting))
            print("self.p: {}".format(self.p))
        # print("THE EHHS:")
        # print(ehhs)


if __name__ == '__main__':
    s = Solver()
    ind = Int("i")
    s.add(And(ind >= 0, ind < 4))
    TOKENS = r"(if|then|else|while|do|skip)(?![\w\d_])   (?P<id>[^\W\d]\w*)   (?P<num>[+\-]?\d+)  " \
             r" (?P<op>[!<>]=|([+\-*/<>])|==)    [();]  =".split()
    GRAMMAR = r"""
    S   ->   S1     |   S1 ; S
    S1  ->   skip   |   id = E   |   if E then S else S1   |   while E do S1
    S1  ->   ( S )
    E   ->   E0   |   E0 op E0 
    E0  ->   id   |   num
    E0  ->   ( E )
    VAR -> x | y | z | i | w | n | myList
    """
    bt = BottomUp(grammar=GRAMMAR, prog_states_file="programStates.txt", tokens=TOKENS, prog_file="TestInv.py")
    print("Vars:")
    print(bt.p)
    print("Tokens:")
    print(bt.tokens)
    print("used_tokens_dict")
    print(bt.used_tokens_dict)
    ois = []
    for bts in bt.bottom_up():
        # print(bts)
        ois.append(bts)
    print("---------------------------------------------------------------------------------------------------------\nois:")
    print(ois)
    # TODO: I' (the invariant with renaming each v to v')

    # for state in bt.get_parsed_states():
    #     s.add(state)
    #     print("---------------------------------------------------------------------")
    #     print(s)
    #     print(s.check())
    #     print(s.model())
    #     s.reset()
    #     s.add(And(I >= 0, I < 4))
    #     print("---------------------------------------------------------------------")
