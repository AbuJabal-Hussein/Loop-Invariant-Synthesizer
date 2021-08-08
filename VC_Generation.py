from syntax import PythonParser, read_source_file
import operator
from z3 import Int, ForAll, Implies, Not, And, Or, Solver, unsat, sat, IntSort, Bool, BoolSort, String, StringSort, \
    Array, IntVector, ArraySort, StringVal, ArithRef, ArrayRef, SeqRef, is_array, BoolRef

OP = {'+': operator.add, '-': operator.sub,
      '*': operator.mul, '/': operator.floordiv,
      '!=': operator.ne, '>': operator.gt, '<': operator.lt,
      '<=': operator.le, '>=': operator.ge, '==': operator.eq,
      'AND': And, 'OR': Or}


# todo: edit this to include more types and tagged variables
# def mk_env(pvars):
#     pvars = pvars + [v + '_' for v in pvars]
#     vars_dict = {v: Int(v) for v in pvars if v not in ['myList', 'myList_']}
#     vars_dict['myList'] = Array('myList', IntSort(), IntSort())
#     vars_dict['myList_'] = Array('myList_', IntSort(), IntSort())
#     return vars_dict


class VCGenerator(object):

    def __init__(self):
        self.parser = PythonParser()

    def __call__(self, input_code):
        ast = self.parser(input_code)
        if ast is None:
            print(">> Invalid program.")
            return None
        print(">> Valid program.")
        print(ast)

        pre_loop, loop_cond, loop_body, post_loop = self.generate_vc(ast)
        print(pre_loop)
        print(loop_cond)
        print(loop_body)
        print(post_loop)

    # def break_down_loop(self, ast):
    #     def find_loop_node_parent(t):
    #         for node in t.subtrees:
    #             if node.root == 'while':
    #                 return t
    #         for node in t.subtrees:
    #             res = find_loop_node_parent(node)
    #             if res:
    #                 return res
    #         return None
    #
    #     while_node_parent = find_loop_node_parent(ast)
    #     if while_node_parent is None:
    #         return None
    #     return while_node_parent.subtrees

    def generate_vc(self, ast):

        def gen_pvars():
            v = ast.before_leaves
            print('-------------')
            print(v)


        def gen_name():
            num = 0
            while True:
                yield 'v_' + str(num)
                num += 1

        gen_var = gen_name()

        def get_expr_type(expr, eval_items):
            if expr.subtrees[0].root == 'ID':
                item_type = vars_dict[str(eval_items[0]) + '_'][1]
            elif expr.subtrees[0].root in ['LIST_E', 'reverse']:
                item_type = ArraySort(IntSort(), eval_items[0][2])
            elif isinstance(eval_items[0], int):
                item_type = IntSort()
            elif isinstance(eval_items[0], bool):
                item_type = BoolSort()
            elif isinstance(eval_items[0], str):
                item_type = StringSort()
            else:
                item_type = IntSort()
            return item_type

        def eval_expr(expr, tagged_id=False):
            if expr.root == 'ID':
                var_name = expr.subtrees[0].root
                var_name = var_name if not tagged_id else var_name + '_'
                return vars_dict[var_name][0]

            elif expr.root in ['NUM', 'BOOL']:
                return expr.subtrees[0].root

            elif expr.root == 'STR':
                return StringVal(expr.subtrees[0].root[1:-1])

            elif expr.root in OP:
                expr1 = expr.subtrees[0]
                expr2 = expr.subtrees[1]
                return OP[expr.root](eval_expr(expr1, tagged_id=tagged_id), eval_expr(expr2, tagged_id=tagged_id))

            elif expr.root == 'NOT':
                expr1 = expr.subtrees[0]
                return Not(eval_expr(expr1))

            elif expr.root == '=':
                expr1 = expr.subtrees[0]
                expr2 = expr.subtrees[1]
                var_name = expr1.subtrees[0].root
                eval_rhs = eval_expr(expr2, tagged_id=False)
                if expr2.root == 'NUM' or isinstance(eval_rhs, ArithRef):
                    vars_dict[var_name] = (Int(var_name), IntSort(), 1)
                    vars_dict[var_name + '_'] = (Int(var_name + '_'), IntSort(), 1)
                elif expr2.root == 'STR':
                    vars_dict[var_name] = (String(var_name), StringSort(), 1)
                    vars_dict[var_name + '_'] = (String(var_name + '_'), StringSort(), 1)
                elif expr2.root == "BOOL" or isinstance(eval_rhs, BoolRef):
                    vars_dict[var_name] = (Bool(var_name), BoolSort(), 1)
                    vars_dict[var_name + '_'] = (Bool(var_name + '_'), BoolSort(), 1)
                elif expr2.root in ['LIST_E', 'reverse']:
                    vars_dict[var_name] = (Array(var_name, IntSort(), eval_rhs[2]), ArraySort(IntSort(), eval_rhs[2]), len(expr2.subtrees)) #todo: should change tuple to list.. so we can change the arr_len later on
                    vars_dict[var_name + '_'] = (Array(var_name + '_', IntSort(), eval_rhs[2]), ArraySort(IntSort(), eval_rhs[2]), len(expr2.subtrees))

                eval_lhs = eval_expr(expr1, tagged_id=True)
                if expr2.root in ['LIST_E', 'reverse']:
                    return And(OP['=='](eval_lhs, eval_rhs[1]), eval_rhs[0])
                else:
                    return OP['=='](eval_lhs, eval_rhs)

            elif expr.root in ['+=', '-=', '*=', '/=']:
                expr1 = expr.subtrees[0]
                expr2 = expr.subtrees[1]
                eval_lhs = eval_expr(expr1, tagged_id=True)
                eval_rhs = eval_expr(expr2, tagged_id=False)
                return OP['=='](eval_lhs, OP[expr.root[0]](eval_lhs, eval_rhs))

            elif expr.root == 'DEREF':  # if this doesnt work, try operator.getitem and operator.setitem
                lst_id = expr.subtrees[0]
                index = expr.subtrees[1]
                eval_id = eval_expr(lst_id,
                                    tagged_id=False)  # maybe we should leave tagged_id without change (as set by the caller). this should allow a[i] to be on LHS if needed.. im not sure though
                eval_index = eval_expr(index, tagged_id=False)
                return eval_id[eval_index]

            elif expr.root == 'LIST_E':
                if len(expr.subtrees) == 0:
                    arr = IntVector(next(gen_var), 0)
                    return True, arr, IntSort(), 0

                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]
                # what happens if the list is empty?
                # should we use Array or IntVector?
                # it is said to be much more efficient to use list comprehension in small finite collection of values
                # note: we assume that all the list items have the same type..
                # item_type = type(eval_items[0])
                item_type = get_expr_type(expr, eval_items)

                arr = Array(next(gen_var), IntSort(), item_type)
                arr_len = len(eval_items)
                if expr.subtrees[0].root != 'LIST_E':
                    arr_value = And([arr[i] == eval_items[i] for i in range(arr_len)])
                else:
                    arr_value = And([And(eval_items[i][0], arr[i] == eval_items[i][1]) for i in range(arr_len)])
                return arr_value, arr, item_type, arr_len

            elif expr.root == 'reverse':
                if len(expr.subtrees) == 0:
                    arr = IntVector(next(gen_var), 0)
                    return True, arr, IntSort(), 0

                # ideally, there should be only one subtree.. and it should be a concrete list or a list variable
                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]

                if expr.subtrees[0].root == 'ID':
                    var_name = expr.subtrees[0].subtrees[0].root
                    arr2 = vars_dict[var_name][0]
                    arr_len = vars_dict[var_name][2]
                    item_type = arr2.range()
                elif expr.subtrees[0].root in ['LIST_E', 'reverse']:
                    arr2 = eval_items[0][1]
                    arr_len = eval_items[0][3]
                    item_type = eval_items[0][2]
                else:
                    arr2 = IntVector(next(gen_var), 0)
                    arr_len = 0
                    item_type = IntSort()

                arr = Array(next(gen_var), IntSort(), item_type)
                print(arr2)
                print(arr_len)
                print(arr2.range())

                if expr.subtrees[0].root not in ['LIST_E', 'reverse']:
                    arr_value = And([arr[i] == arr2[arr_len - i - 1] for i in range(arr_len)])
                else:
                    arr_value = And(eval_items[0][0], And([arr[i] == arr2[arr_len - i - 1] for i in range(arr_len)]))

                return arr_value, arr, item_type, arr_len

            return True

        def construct_tr(t):
            # here evaluate the statements, and in eval_expr evaluate the expressions

            if t.root == 'S' and len(t.subtrees) > 0 and t.subtrees[0].root == 'while':
                # process the while body
                tr_lists[1] = construct_tr(t.subtrees[0])
                # process the statements after the while, if exists
                if len(t.subtrees) == 2:
                    tr_lists[2] = construct_tr(t.subtrees[1])
                return True
            elif t.root == 'S':
                if len(t.subtrees) == 1:
                    return construct_tr(t.subtrees[0])
                return And(construct_tr(t.subtrees[0]), construct_tr(t.subtrees[1]))
            elif t.root == 'while':
                cond = eval_expr(t.subtrees[0])
                return [cond, construct_tr(t.subtrees[1])]

            elif t.root in ['if', 'elif']:
                cond = eval_expr(t.subtrees[0])
                body = construct_tr(t.subtrees[1])
                if len(t.subtrees) == 3:
                    elif_body = construct_tr(t.subtrees[2])
                    return And(Implies(cond, body), Implies(Not(cond), elif_body))
                return And(Implies(cond, body),
                           Implies(Not(cond), Not(body)))  # todo: change Not(body) to something else, like m_ = m

            elif t.root == 'else':
                return construct_tr(t.subtrees[0])

            elif t.root == 'BLOCK':
                if len(t.subtrees) == 1:
                    return construct_tr(t.subtrees[0])
                elif len(t.subtrees) == 2:
                    return And(construct_tr(t.subtrees[0]), construct_tr(t.subtrees[1]))

            elif t.root in ['=', '+=', '-=', '*=', '/=']:
                print('ttttttttttttttttttttt')
                print(t)
                return eval_expr(t)

            # function call statements does not affect the program, assuming that they don't have side effects on the program variables
            # function expressions do affect the program state.. we take care of them in eval_expr
            elif t.root in ['INV_FUNC', 'reverse']:
                return True

            return True

        # todo: extract the pvars from the AST
        # gen_pvars()
        # pvars = ['i', 'n', 'x', 'myList', 'i', 'y']
        # vars_dict = mk_env(pvars)

        vars_dict = {}
        tr_lists = [True, [True, True], True]
        tr_lists[0] = construct_tr(ast)
        return tr_lists[0], tr_lists[1][0], tr_lists[1][1], tr_lists[2]
