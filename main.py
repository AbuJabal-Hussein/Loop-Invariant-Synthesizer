import argparse
from LoopInvSynth import LoopInvSynth
from bottom_up import *
import multiprocessing
# import timeout_decorator
import sys



def get_pre_post_conds(file):
    post_cond_ = pre_cond_ = ""
    with open(file, "r") as reader:
        content = reader.read()
        for line in content.split(sep='\n'):
            var_name, data = line.split(sep=":")
            if var_name == "post_cond":
                post_cond_ = data.strip()
            if var_name == "pre_cond":
                pre_cond_ = data.strip()
        return pre_cond_, post_cond_


def get_grammar_and_tokens(file):
    grammar = tokens = r""
    with open(file, "r") as reader:
        content = reader.read()
        t, g = [x.strip() for x in content.split("GRAMMAR")]
    grammar = r"{}".format(g)
    tokens = r"{}".format(t)
    return grammar.strip(), tokens.strip()


def run(program_file, grammar_file, conds_file):
    prog_states_file = "programStates.txt"
    input_code = read_source_file(program_file)
    LoopInvSynth()(prog_states_file, input_code)
    print("code: {}".format(input_code))
    pre_loop, loop_cond, loop_body, post_loop = VCGenerator()(input_code)
    GRAMMAR, TOKENS = get_grammar_and_tokens(grammar_file)
    TOKENS = TOKENS.split()
    bt = BottomUp(grammar=GRAMMAR, prog_states_file=prog_states_file, tokens=TOKENS, prog_file=program_file)
    pre_cond, post_cond = get_pre_post_conds(conds_file)
    pre_cond, post_cond = bt.batch_to_z3([pre_cond, post_cond]) or True, True
    # print("Vars:")
    # print(bt.p)
    # print("Tokens:")
    # print(bt.tokens)
    # print("used_tokens_dict")
    # print(bt.used_tokens_dict)
    solver = Solver()
    for b in bt.bottom_up():
        inv, inv_tagged = b
        lst = [Implies(And(pre_cond, pre_loop), inv_tagged),
               Implies(And(inv, loop_cond, loop_body), inv_tagged),
               Implies(And(inv, post_loop), post_cond)]
        solver.add(Not(And(lst)))
        if solver.check() == unsat:
            print("Found inv: {}".format(inv))
            return inv
        solver.reset()

LOCAL_TIMEOUT = 20

class TestIntCodes:

    def __init__(self):
        self.startTime = 0
        self.path_prefix = ""
        self.__stdout__ = sys.stdout

    def setUp(self):
        self.startTime = time()
        self.path_prefix = "benchmarks/integers_benchmark/"
        sys.stdout = open(os.devnull, 'w')

    def test1_int(self):
        proc = multiprocessing.Process(target=run, kwargs={"program_file": self.path_prefix + "test1_ints.py",
                                                           "grammar_file": self.path_prefix + "grammar",
                                                           "conds_file": self.path_prefix + "conditions_test1"})
        proc.start()
        proc.join(LOCAL_TIMEOUT)
        if proc.is_alive():
            proc.terminate()
            return False

        # inv = run(self.path_prefix + "test1_ints.py", self.path_prefix + "grammar",
        #           self.path_prefix + "conditions_test1")
        return True

    def test2_int(self):
        inv = run(self.path_prefix + "test2_ints.py", self.path_prefix + "grammar",
                  self.path_prefix + "conditions_test2")
        return True

    def test3_int(self):
        inv = run(self.path_prefix + "test3_ints.py", self.path_prefix + "grammar",
                  self.path_prefix + "conditions_test3")
        return True

    def test4_int(self):
        inv = run(self.path_prefix + "test4_ints.py", self.path_prefix + "grammar",
                  self.path_prefix + "conditions_test4")
        return True

    def test5_int(self):
        inv = run(self.path_prefix + "test5_ints.py", self.path_prefix + "grammar",
                  self.path_prefix + "conditions_test5")
        return True

    def tearDown(self, name):
        sys.stdout = self.__stdout__
        t = time() - self.startTime
        print('%s: %.3f' % (name, t))

    def run(self):
        message = "Passed"
        for test in [self.test1_int, self.test2_int, self.test3_int, self.test4_int, self.test5_int]:
            print("Starting " + test.__name__ + "...")
            err = None
            self.setUp()
            try:
                t = test()
            except Exception as e:
                err = e.args[0]
            if not t:
                message = "Failed"
            else:
                message = "Passed"
            if err:
                message = err
            self.tearDown(test.__name__)
            print(test.__name__ + "..." + str(message))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find Loop invariant of a program. See README for more info')
    parser.add_argument('--program', "-p", type=str, help='Name of the input program file',
                        dest="program_file")
    parser.add_argument('--grammar', "-g", type=str,
                        dest="grammar_file",
                        help='Name of the file containing the grammar and tokens as explained in README')
    # parser.add_argument('--pre_cond', type=str, dest="pre_cond",
    #                     help="The pre condition of the program", default="True")
    # parser.add_argument('--post_cond', type=str, dest="post_cond",
    #                     help="The post condition of the program", default="True")
    parser.add_argument('--conditions', type=str, dest="conds_file",  default="",
                        help="The name of the file containing pre and post condition on the input program")
    parser.add_argument('--tests', help="Run the unittests.",
                        action='store_true')

    args = parser.parse_args()

    if args.tests:
        TestIntCodes().run()
        exit(0)
    if not args.program_file or not args.grammar_file:
        print("error: the following arguments are required: --program/-p, --grammar/-g  OR --tests")
        exit(1)
    run(args.program_file, args.grammar_file, args.conds_file)



    # import z3Test
    # LoopInvSynth()
    # print('PyCharm')
    # prog_file = "benchmarks/test_append.py"
