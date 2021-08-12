from syntax import PythonParser, read_source_file
import operator
from z3 import Int, ForAll, Implies, Not, And, Or, Solver, unsat, sat, IntSort, Bool, BoolSort, String, StringSort, \
    Array, IntVector, ArraySort, StringVal, ArithRef, ArrayRef, SeqRef, is_array, BoolRef

OP = {'+': operator.add, '-': operator.sub,
      '*': operator.mul, '/': operator.floordiv,
      '!=': operator.ne, '>': operator.gt, '<': operator.lt,
      '<=': operator.le, '>=': operator.ge, '==': operator.eq,
      'AND': And, 'OR': Or}




class VCGenerator(object):

    def __init__(self, vars_dict=dict()):
        self.parser = PythonParser()
        self.vars_dict = vars_dict

    def __call__(self, input_code):
        ast = self.parser(input_code)
        if ast is None:
            print(">> Invalid program.")
            return None
        print(">> Valid program.")
        print('ast:')
        print(ast)
        print('')

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

        def eval_expr(expr, tagged_id=False, collected_vars=None):
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
                if expr2.root == 'NUM' or isinstance(eval_rhs, ArithRef) or expr2.root == 'len' or type(eval_rhs) == int:
                    vars_dict[var_name] = [Int(var_name), IntSort(), 1]
                    vars_dict[var_name + '_'] = [Int(var_name + '_'), IntSort(), 1]
                elif expr2.root == 'STR':
                    vars_dict[var_name] = [String(var_name), StringSort(), 1]
                    vars_dict[var_name + '_'] = [String(var_name + '_'), StringSort(), 1]
                elif expr2.root == "BOOL" or isinstance(eval_rhs, BoolRef) or type(eval_rhs) == bool:
                    vars_dict[var_name] = [Bool(var_name), BoolSort(), 1]
                    vars_dict[var_name + '_'] = [Bool(var_name + '_'), BoolSort(), 1]
                elif expr2.root in ['LIST_E', 'reverse']:
                    vars_dict[var_name] = [Array(var_name, IntSort(), eval_rhs[2]), ArraySort(IntSort(), eval_rhs[2]), eval_rhs[3]]
                    vars_dict[var_name + '_'] = [Array(var_name + '_', IntSort(), eval_rhs[2]), ArraySort(IntSort(), eval_rhs[2]), eval_rhs[3]]

                eval_lhs = eval_expr(expr1, tagged_id=True)
                if not(collected_vars is None):
                    collected_vars.append(OP['=='](eval_lhs, eval_expr(expr1, tagged_id=False)))

                if expr2.root in ['LIST_E', 'reverse']:
                    return And(OP['=='](eval_lhs, eval_rhs[1]), eval_rhs[0])
                else:
                    return OP['=='](eval_lhs, eval_rhs)

            elif expr.root in ['+=', '-=', '*=', '/=']:
                expr1 = expr.subtrees[0]
                expr2 = expr.subtrees[1]
                eval_lhs = eval_expr(expr1, tagged_id=True)
                eval_rhs = eval_expr(expr2, tagged_id=False)
                if collected_vars is not None:
                    collected_vars.append(OP['=='](eval_lhs, eval_expr(expr1, tagged_id=False)))
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
                    # arr = IntVector(next(gen_var), 0)
                    arr = Array(next(gen_var), IntSort(), IntSort())
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
                if expr.subtrees[0].root not in ['LIST_E', 'reverse']:
                    arr_value = And([arr[i] == arr2[arr_len - i - 1] for i in range(arr_len)])
                else:
                    arr_value = And(eval_items[0][0], And([arr[i] == arr2[arr_len - i - 1] for i in range(arr_len)]))

                return arr_value, arr, item_type, arr_len

            elif expr.root == 'len':
                len_var = Int(next(gen_var))
                lst_eval = (eval_expr(expr.subtrees[0]))
                if isinstance(lst_eval, list):
                    return lst_eval[3]
                return vars_dict[str(lst_eval)][2]

            return True

        def construct_tr(t, collected_vars=None):
            # here evaluate the statements, and in eval_expr evaluate the expressions

            if t.root == 'S' and len(t.subtrees) > 0 and t.subtrees[0].root == 'while':
                # process the while body
                tr_lists[1] = construct_tr(t.subtrees[0], collected_vars=collected_vars)
                # process the statements after the while, if exists
                if len(t.subtrees) == 2:
                    tr_lists[2] = construct_tr(t.subtrees[1], collected_vars=collected_vars)
                return True
            elif t.root == 'S':
                if len(t.subtrees) == 1:
                    return construct_tr(t.subtrees[0], collected_vars=collected_vars)
                # this case happens when the while is the last statement in the program
                if t.subtrees[1].root == 'while':
                    res = construct_tr(t.subtrees[0], collected_vars=collected_vars)
                    tr_lists[1] = construct_tr(t.subtrees[1], collected_vars=collected_vars)
                    return res
                return And(construct_tr(t.subtrees[0], collected_vars=collected_vars), construct_tr(t.subtrees[1], collected_vars=collected_vars))
            elif t.root == 'while':
                cond = eval_expr(t.subtrees[0])
                return [cond, construct_tr(t.subtrees[1], collected_vars=collected_vars)]

            elif t.root in ['if', 'elif']:
                cond = eval_expr(t.subtrees[0])
                if len(t.subtrees) == 3:
                    body = construct_tr(t.subtrees[1], collected_vars=collected_vars)
                    elif_body = construct_tr(t.subtrees[2], collected_vars=collected_vars)
                    return And(Implies(cond, body), Implies(Not(cond), elif_body))
                assigned_vars = []
                body = construct_tr(t.subtrees[1], assigned_vars)
                unchanged_vars = And(assigned_vars)
                return And(Implies(cond, body),
                           Implies(Not(cond), unchanged_vars))

            elif t.root == 'else':
                return construct_tr(t.subtrees[0], collected_vars=collected_vars)

            elif t.root == 'BLOCK':
                if len(t.subtrees) == 1:
                    return construct_tr(t.subtrees[0], collected_vars=collected_vars)
                elif len(t.subtrees) == 2:
                    return And(construct_tr(t.subtrees[0], collected_vars=collected_vars), construct_tr(t.subtrees[1], collected_vars=collected_vars))

            elif t.root in ['=', '+=', '-=', '*=', '/=', '>', '<', '>=', "<="]:
                return eval_expr(t, collected_vars=collected_vars)

            # function call statements does not affect the program, assuming that they don't have side effects on the program variables
            # function expressions do affect the program state.. we take care of them in eval_expr
            elif t.root in ['INV_FUNC', 'reverse', 'len']:
                return True

            return True


        vars_dict = self.vars_dict.copy()
        tr_lists = [True, [True, True], True]
        tr_lists[0] = construct_tr(ast)
        return tr_lists[0], tr_lists[1][0], tr_lists[1][1], tr_lists[2]
