import argparse
from LoopInvSynth import LoopInvSynth
from bottom_up import *


def get_pre_post_conds(file):
    post_cond_ = pre_cond_ = ""
    with open(file, "r") as reader:
        content = reader.read()
        for line in content.split(sep='\n'):
            var_name, data = line.split(sep="=")
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find Loop invariant of a program. See README for more info')
    parser.add_argument('--program', "-p", type=str, help='Name of the input program file',
                        required=True, dest="program_file")
    parser.add_argument('--grammar', "-g", type=str,
                        required=True, dest="grammar_file",
                        help='Name of the file containing the grammar and tokens as explained in README')
    # parser.add_argument('--pre_cond', type=str, dest="pre_cond",
    #                     help="The pre condition of the program", default="True")
    # parser.add_argument('--post_cond', type=str, dest="post_cond",
    #                     help="The post condition of the program", default="True")
    parser.add_argument('--conditions', type=str, dest="conds_file",  default="",
                        help="The name of the file containing pre and post condition on the input program")

    args = parser.parse_args()
    prog_states_file = "programStates.txt"
    input_code = read_source_file(args.program_file)
    LoopInvSynth()(prog_states_file, input_code)
    pre_loop, loop_cond, loop_body, post_loop = VCGenerator()(input_code)
    # TODO: Extract grammar and tokens from file args.grammar_file into:
    GRAMMAR, TOKENS = get_grammar_and_tokens(args.grammar_file)
    TOKENS = TOKENS.split()

    bt = BottomUp(grammar=GRAMMAR, prog_states_file=prog_states_file, tokens=TOKENS, prog_file=args.program_file)
    pre_cond, post_cond = get_pre_post_conds(args.conds_file)  # TODO: Parse into z3
    pre_cond, post_cond = bt.batch_to_z3([pre_cond, post_cond]) or True, True

    print("Vars:")
    print(bt.p)
    print("Tokens:")
    print(bt.tokens)
    print("used_tokens_dict")
    print(bt.used_tokens_dict)

    solver = Solver()
    for b in bt.bottom_up():
        inv, inv_tagged = b
        lst = [Implies(And(pre_cond, pre_loop), inv_tagged),
               Implies(And(inv, loop_cond, loop_body), inv_tagged),
               Implies(And(inv, post_loop), post_cond)]
        solver.add(Not(And(lst)))
        if solver.check() == unsat:
            print("Found inv: {}".format(inv))
            # TODO: Print to file
            break
        solver.reset()

    # import z3Test
    # LoopInvSynth()
    # print('PyCharm')
    # prog_file = "benchmarks/test_append.py"



