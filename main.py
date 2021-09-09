import argparse
from LoopInvSynth import LoopInvSynth
from bottom_up import *
import multiprocessing
import os
# import timeout_decorator
import sys

def get_neg_examples(file):
    negative_examples = []
    with open(file, "r") as reader:
        content = reader.read().strip()
        for line in content.split(sep='\n'):
            negative_examples.append(line)


def get_pre_post_conds(file):
    post_cond_ = pre_cond_ = ""
    with open(file, "r") as reader:
        content = reader.read().strip()
        for line in content.split(sep='\n'):
            var_name, data = line.split(sep=":")
            if var_name.strip() == "post_cond":
                post_cond_ = data.strip()
            elif var_name.strip() == "pre_cond":
                pre_cond_ = data.strip()

        return pre_cond_, post_cond_


def get_grammar(file):
    grammar = r""
    with open(file, "r") as reader:
        content = reader.read()
    grammar = r"{}".format(content.strip())
    return grammar.strip()


def run(program_file, grammar_file, conds_file, omit_print=False, res_dict=None, timeout=-1, examples_file=''):
    back_up = sys.stdout
    if omit_print:
        sys.stdout = open(os.devnull, 'w')
    prog_states_file = "programStates.txt"
    input_code = read_source_file(program_file)
    LoopInvSynth()(prog_states_file, input_code)
    print("code: {}".format(input_code))
    pre_loop, loop_cond, loop_body, post_loop = VCGenerator()(input_code)
    GRAMMAR = get_grammar(grammar_file)
    TOKENS = r" (if|else|elif|while|for|in)(?![\w\d_]) (?P<COMMA>\,) (?P<DOT>\.) (?P<LPAREN>\() (?P<NUM>[+\-]?\d+)" \
             r" (?P<ASSOPPOWER>(\*\*=)) (?P<ASSOP>[+\-*/]=) (?P<POWER>(\*\*)) (?P<MULTDIV>[*/%]) (?P<PLUSMINUS>[+\-])  :" \
             r" (?P<RPAREN>\)) (?P<LSPAREN>\[) (?P<RSPAREN>\]) " \
             r" (?P<NOT>not) (?P<FALSE>False) (?P<TRUE>True) " \
             r" (?P<LEN>len) (?P<INV>__inv__) (?P<REVERSE>reverse) (?P<APPEND>append) (?P<MAX>max)" \
             r" (?P<MIN>min) (?P<INDEX>index) (?P<SUBSTRING>substring) (?P<INT>int) (?P<BOOLTYPE>bool) (?P<CHARAT>charAt) " \
             r" (?P<ALL>all) (?P<ANY>any) (?P<SUM>sum) (?P<RANGE>range)" \
             r" (?P<STR1>\'([^\n\r\"\'\\]|\\[rnt\"\'\\])*\') (?P<STR2>\"([^\n\r\"\'\\]|\\[rnt\"\'\\])*\") " \
             r" (?P<RELOP>[!<>=]=|([<>])) (?P<AND>and) (?P<OR>or) (?P<ID>[^\W\d]\w*) (?P<NEWLINE>[\r\n(\r\n)]+) " \
             r" (?P<INDENT5>(\t\t\t\t\t)) (?P<INDENT4>(\t\t\t\t)) (?P<INDENT3>(\t\t\t)) " \
             r" (?P<INDENT2>(\t\t)) (?P<INDENT>(\t))  =".split()
    bt = BottomUp(grammar=GRAMMAR, prog_states_file=prog_states_file, tokens=TOKENS, prog_file=program_file,
                  timeout=timeout)
    if examples_file:
        bt_examples = BottomUp(grammar=GRAMMAR, prog_states_file=examples_file, tokens=TOKENS, prog_file=program_file,
                               timeout=timeout, examplesParsingMode=True)
        examples = deepcopy(bt_examples.examples)
        bt.update_examples(examples)

    print("Bottom up's program states parsing: {}".format(bt.program_states))
    pre_cond, post_cond = get_pre_post_conds(conds_file)
    pre_cond = bt.str_to_z3(pre_cond)
    post_cond = bt.str_to_z3(post_cond)
    pre_cond = pre_cond if pre_cond is not None else True
    post_cond = post_cond if post_cond is not None else True
    if type(post_cond) is not bool:
        tagged_post_cond = bt.tag_and_convert(post_cond)
    else:
        tagged_post_cond = post_cond
    print('pre_cond: {}'.format(pre_cond))
    print('post condition: {}'.format(tagged_post_cond))
    # print("Vars:")
    # print(bt.p)
    # print("Tokens:")
    # print(bt.tokens)
    # print("used_tokens_dict")
    # print(bt.used_tokens_dict)
    solver = Solver()
    for b in bt.bottom_up():
        # if b == "timed out":
        #     sys.stdout = back_up
        #     print("timed out")
        #     if res_dict:
        #         res_dict["result"] = b
        #     print("res_dict['result']: {}".format(res_dict["result"]))
        #     return False
        inv, inv_tagged = b
        lst = [Implies(And(pre_cond, pre_loop), inv_tagged),
               Implies(And(inv, loop_cond, loop_body), inv_tagged),
               Implies(And(inv, Not(loop_cond), post_loop), tagged_post_cond)]
        solver.add(Not(And(lst)))
        if solver.check() == unsat:
            sys.stdout = back_up
            print("Found inv: {}".format(inv))
            if res_dict:
                res_dict["result"] = ("Found inv: {}".format(inv))
            # print("res_dict['result']: {}".format(res_dict["result"]))
            return inv
        solver.reset()
    sys.stdout = back_up
    if res_dict:
        res_dict["result"] = "No Inv found or timed out"
    return False


LOCAL_TIMEOUT = 60 * 8


class TestIntCodes:

    def __init__(self):
        self.startTime = 0
        self.path_prefix = ""
        self.__stdout__ = sys.stdout

    def setUp(self):
        self.startTime = time()
        self.path_prefix = "benchmarks/integers_benchmarks/"

    def test1_int(self):
        res_dict = dict()
        inv = None
        proc = multiprocessing.Process(target=run, kwargs={"program_file": self.path_prefix + "test1_ints.py",
                                                           "grammar_file": self.path_prefix + "grammar",
                                                           "conds_file": self.path_prefix + "conditions_test1",
                                                           "omit_print": True,
                                                           "res_dict": res_dict,
                                                           "timeout": LOCAL_TIMEOUT})
        proc.start()
        proc.join(LOCAL_TIMEOUT)
        if proc.is_alive():
            try:
                proc.terminate()
            except multiprocessing.ProcessError as e:
                print("---Timed out---")
            return False
        if res_dict["result"] != inv:
            return False

        return True

    def test2_int(self):
        res_dict = dict()
        x = Int("x")
        inv = x > 0
        proc = multiprocessing.Process(target=run, kwargs={"program_file": self.path_prefix + "test2_ints.py",
                                                           "grammar_file": self.path_prefix + "grammar",
                                                           "conds_file": self.path_prefix + "conditions_test2",
                                                           "omit_print": True,
                                                           "res_dict": res_dict,
                                                           "timeout": LOCAL_TIMEOUT})
        proc.start()
        proc.join(LOCAL_TIMEOUT)
        if proc.is_alive():
            try:
                proc.terminate()
            except Exception as e:
                print(e)
            return False
        if res_dict["result"] != inv:
            return False

        return True

    def test3_int(self):
        res_dict = dict()
        x = Int("x")
        inv = x > 0
        proc = multiprocessing.Process(target=run, kwargs={"program_file": self.path_prefix + "test3_ints.py",
                                                           "grammar_file": self.path_prefix + "grammar",
                                                           "conds_file": self.path_prefix + "conditions_test3",
                                                           "omit_print": True,
                                                           "res_dict": res_dict,
                                                           "timeout": LOCAL_TIMEOUT})
        proc.start()
        proc.join(LOCAL_TIMEOUT)
        if proc.is_alive():
            try:
                proc.terminate()
            except Exception as e:
                print(e)
            return False
        if res_dict["result"] != inv:
            print("Got res: {}".format(res_dict["result"]))
            return False

        return True

    def test4_int(self):
        res_dict = dict()
        x = Int("x")
        inv = x > 0
        proc = multiprocessing.Process(target=run, kwargs={"program_file": self.path_prefix + "test4_ints.py",
                                                           "grammar_file": self.path_prefix + "grammar",
                                                           "conds_file": self.path_prefix + "conditions_test4",
                                                           "omit_print": True,
                                                           "res_dict": res_dict,
                                                           "timeout": LOCAL_TIMEOUT})
        proc.start()
        proc.join(LOCAL_TIMEOUT)
        if proc.is_alive():
            try:
                proc.terminate()
            except Exception as e:
                print(e)
            return False
        if res_dict["result"] != inv:
            print("Got res: {}".format(res_dict["result"]))
            return False

        return True

    def test5_int(self):
        res_dict = dict()
        x = Int("x")
        inv = x > 0
        proc = multiprocessing.Process(target=run, kwargs={"program_file": self.path_prefix + "test5_ints.py",
                                                           "grammar_file": self.path_prefix + "grammar",
                                                           "conds_file": self.path_prefix + "conditions_test5",
                                                           "omit_print": True,
                                                           "res_dict": res_dict,
                                                           "timeout": LOCAL_TIMEOUT})
        proc.start()
        proc.join(LOCAL_TIMEOUT)
        if proc.is_alive():
            try:
                proc.terminate()
            except Exception as e:
                print(e)
            return False
        if res_dict["result"] != inv:
            print("Got res: {}".format(res_dict["result"]))
            return False

        return True

    def tearDown(self, name):
        t = time() - self.startTime
        print('%s: %.3f' % (name, t))

    def run(self):
        for test in [self.test1_int, self.test2_int, self.test3_int, self.test4_int, self.test5_int]:
            print("------------------------------------------------------------------------------------"
                  "----------------------------------------------------")
            print("Starting " + test.__name__ + "...")
            err = None
            self.setUp()
            t = None
            try:
                t = test()
            except Exception as e:
                err = e.args[0]
            if not t:
                message = "Failed"
            else:
                message = t
            if err:
                message = err
            print(test.__name__ + ": " + str(message))
            self.tearDown(test.__name__)


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
    parser.add_argument('-t', '--time-out', help="Max run time in minutes(7 Minutes default)\n"
                                                 "Max run time for each test in case --tests was supplied",
                        type=float, default=8.00, dest="timeout")
    parser.add_argument('--examples-file', '-e', help="The name of the file containing the negative examples.",
                        type=str, dest="examples_file")

    args = parser.parse_args()
    if args.timeout == 0:
        args.timeout = 1
    if args.tests:
        from tests import run_tests
        run_tests(timeout=args.timeout)
        exit(0)
    if not args.program_file or not args.grammar_file:
        print("error: the following arguments are required: --program/-p, --grammar/-g  OR --tests")
        exit(1)

    run(args.program_file, args.grammar_file, args.conds_file, timeout=args.timeout * 60,
        examples_file=args.examples_file)
