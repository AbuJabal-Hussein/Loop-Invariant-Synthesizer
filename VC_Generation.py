from syntax import PythonParser, read_source_file
import operator
from z3 import Int, ForAll, Implies, Not, And, Or, Solver, unsat, sat, IntSort, Bool, BoolSort, String, StringSort, \
    Array, IntVector, ArraySort, StringVal, ArithRef, ArrayRef, SeqRef, is_array, BoolRef, is_string_value, Length, \
    is_string, is_int, If, IndexOf, Exists, simplify, Real, RealVal, Q, z3types, SubString, Sum, is_bv, Unit, BitVecRef

OP = {'+': operator.add, '-': operator.sub,
      '*': operator.mul, '/': (lambda a, b: a / b),
      '%': operator.mod, '**': operator.pow,
      '!=': operator.ne, '>': operator.gt, '<': operator.lt,
      '<=': operator.le, '>=': operator.ge, '==': operator.eq,
      'AND': And, 'OR': Or}




class VCGenerator(object):

    def __init__(self, vars_dict=dict(), vars_noz3=dict(), should_tag=True):
        self.parser = PythonParser()
        self.vars_dict = vars_dict
        self.vars_noz3 = vars_noz3
        self.should_tag = should_tag

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
        return pre_loop, loop_cond, loop_body, post_loop

    def create_var(self, id_type, var_name):
        if id_type == IntSort():
            return Int(var_name)
        elif id_type == BoolSort():
            return Bool(var_name)
        elif id_type == StringSort():
            return String(var_name)
        elif id_type == ArraySort(IntSort(), IntSort()):
            return Array(var_name, IntSort(), IntSort())
        elif id_type == ArraySort(IntSort(), BoolSort()):
            return Array(var_name, IntSort(), BoolSort())
        elif id_type == ArraySort(IntSort(), StringSort()):
            return Array(var_name, IntSort(), StringSort())
        elif id_type == ArraySort(IntSort(), ArraySort(IntSort(), IntSort())):
            return Array(var_name, IntSort(), ArraySort(IntSort(), IntSort()))
        elif id_type == ArraySort(IntSort(), ArraySort(IntSort(), BoolSort())):
            return Array(var_name, IntSort(), ArraySort(IntSort(), BoolSort()))
        elif id_type == ArraySort(IntSort(), ArraySort(IntSort(), StringSort())):
            return Array(var_name, IntSort(), ArraySort(IntSort(), StringSort()))

        return Int(var_name)

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
        list_types = ['LIST_E', 'LIST_COMPREHENSION', 'reverse', 'append', 'remove', 'range']
        bool_types = ['BOOL', 'all', 'any']
        string_types = ['STR', 'charAt', 'substring']

        def get_expr_type(expr, eval_item):
            if expr.root == 'ID':
                item_type = vars_dict[str(eval_item)][1]
            elif expr.root in list_types:
                item_type = ArraySort(IntSort(), eval_item[2])
            elif expr_is_int(expr, eval_item):
                item_type = IntSort()
            elif isinstance(eval_item, bool) or isinstance(eval_item, BoolRef) or expr.root in bool_types:
                item_type = BoolSort()
            elif is_string(eval_item) or expr.root in string_types:
                item_type = StringSort()
            else:
                item_type = IntSort()
            return item_type


        def expr_is_int(expr, expr_eval):
            return is_int(expr_eval) or \
                   isinstance(expr_eval, int) or \
                   isinstance(expr_eval, ArithRef) or \
                   expr.root in ['NUM', 'len', 'max', 'min', 'index', 'sum']

        def eval_expr(expr, tagged_id=False, collected_vars=None):
            tagged_id = self.should_tag if not self.should_tag else tagged_id
            if expr.root == 'ID':
                var_name = expr.subtrees[0].root
                var_name = var_name if not tagged_id else var_name + '_'
                if var_name in vars_dict:
                    return vars_dict[var_name][0]
                if self.vars_noz3[var_name][2] > 1:
                    return Array(var_name, IntSort(), self.vars_noz3[var_name][0]())
                return self.vars_noz3[var_name][0](var_name)

            elif expr.root in ['NUM', 'BOOL']:
                return expr.subtrees[0].root

            elif expr.root == 'STR':
                return StringVal(expr.subtrees[0].root[1:-1])

            elif expr.root in OP:
                expr1 = expr.subtrees[0]
                expr2 = expr.subtrees[1]
                expr1_eval = eval_expr(expr1, tagged_id=False)
                expr2_eval = eval_expr(expr2, tagged_id=False)
                items_vc = []
                item1 = expr1_eval
                item2 = expr2_eval
                if type(expr1_eval) is tuple:
                    item1 = expr1_eval[1]
                    items_vc.append(expr1_eval[0])
                if type(expr2_eval) is tuple:
                    item2 = expr2_eval[1]
                    items_vc.append(expr2_eval[0])

                if items_vc:
                    if expr.root in ['!=', '>', '<', '<=', '>=', '==', 'AND', 'OR']:
                        return And(items_vc + [OP[expr.root](item1, item2)])
                    return And(items_vc), OP[expr.root](item1, item2)
                return OP[expr.root](item1, item2)

            elif expr.root == 'NOT':
                expr1 = expr.subtrees[0]
                return Not(eval_expr(expr1))

            elif expr.root == '=':
                expr1 = expr.subtrees[0]
                expr2 = expr.subtrees[1]
                var_name = expr1.subtrees[0].root
                eval_rhs = eval_expr(expr2, tagged_id=False)
                if expr2.root == "BOOL" or isinstance(eval_rhs, BoolRef) or type(eval_rhs) == bool:
                    vars_dict[var_name] = [Bool(var_name), BoolSort(), 1]
                    vars_dict[var_name + '_'] = [Bool(var_name + '_'), BoolSort(), 1]
                elif expr2.root == 'NUM' or expr_is_int(expr2, eval_rhs):
                    vars_dict[var_name] = [Int(var_name), IntSort(), 1]
                    vars_dict[var_name + '_'] = [Int(var_name + '_'), IntSort(), 1]
                elif expr2.root == 'STR' or expr2.root in string_types:
                    vars_dict[var_name] = [String(var_name), StringSort(), 1]
                    vars_dict[var_name + '_'] = [String(var_name + '_'), StringSort(), 1]
                elif expr2.root in list_types:
                    vars_dict[var_name] = [Array(var_name, IntSort(), eval_rhs[2]), ArraySort(IntSort(), eval_rhs[2]), eval_rhs[3]]
                    vars_dict[var_name + '_'] = [Array(var_name + '_', IntSort(), eval_rhs[2]), ArraySort(IntSort(), eval_rhs[2]), eval_rhs[3]]
                elif expr2.root == "ID":
                    rhs_var_name = expr2.subtrees[0].root
                    rhs_var_type = vars_dict[rhs_var_name][1]
                    rhs_var_len = vars_dict[rhs_var_name][2]
                    vars_dict[var_name] = [self.create_var(rhs_var_type, var_name), rhs_var_type, rhs_var_len]
                    vars_dict[var_name + '_'] = [self.create_var(rhs_var_type, var_name + '_'), rhs_var_type, rhs_var_len]
                elif type(eval_rhs) is tuple:
                    rhs_var_type = get_expr_type(expr2, eval_rhs[1])
                    vars_dict[var_name] = [self.create_var(rhs_var_type, var_name), rhs_var_type, 1]
                    vars_dict[var_name + '_'] = [self.create_var(rhs_var_type, var_name + '_'), rhs_var_type, 1]

                eval_lhs = eval_expr(expr1, tagged_id=True)
                if not(collected_vars is None):
                    collected_vars.append(OP['=='](eval_lhs, eval_expr(expr1, tagged_id=False)))
                eq_vc = []
                if type(eval_lhs) is tuple:
                    eq_vc.append(eval_lhs[0])
                    eval_lhs = eval_lhs[1]

                if expr2.root in list_types or type(eval_rhs) is tuple:
                    eq_vc.append(eval_rhs[0])
                    eval_rhs = eval_rhs[1]

                if eq_vc:
                    return And(eq_vc + [OP['=='](eval_lhs, eval_rhs)])
                else:
                    return OP['=='](eval_lhs, eval_rhs)

            elif expr.root in ['+=', '-=', '*=', '/=', '**=']:
                expr1 = expr.subtrees[0]
                expr2 = expr.subtrees[1]
                eval_lhs = eval_expr(expr1, tagged_id=True)
                eval_lhs_untagged = eval_expr(expr1, tagged_id=False)
                eval_rhs = eval_expr(expr2, tagged_id=False)
                if collected_vars is not None:
                    collected_vars.append(OP['=='](eval_lhs, eval_expr(expr1, tagged_id=False)))
                item_rhs = eval_rhs
                item_lhs = eval_lhs
                item_lhs_untagged = eval_lhs_untagged
                items_vc = []
                if type(item_rhs) is tuple:
                    item_rhs = eval_rhs[1]
                    items_vc.append(eval_rhs[0])
                if type(item_lhs) is tuple:
                    item_lhs = eval_lhs[1]
                    item_lhs_untagged = eval_lhs_untagged[1]
                    items_vc.append(eval_lhs[0])
                    # items_vc.append(eval_lhs_untagged[0])

                assign_vc = OP['=='](item_lhs, OP[expr.root[:-1]](item_lhs, item_rhs))
                if len(items_vc) > 0:
                    assign_vc = And(items_vc + [assign_vc])
                return assign_vc

            elif expr.root == 'DEREF':  # if this doesnt work, try operator.getitem and operator.setitem
                lst_id = expr.subtrees[0]
                index = expr.subtrees[1]
                eval_id = eval_expr(lst_id,
                                    tagged_id=False)  # maybe we should leave tagged_id without change (as set by the caller). this should allow a[i] to be on LHS if needed.. im not sure though
                eval_index = eval_expr(index, tagged_id=False)
                if type(eval_index) is tuple:
                    deref = eval_id[eval_index[1]]
                    if isinstance(deref, BitVecRef):
                        deref = Unit(deref)
                    return eval_index[0], deref
                deref = eval_id[eval_index]
                if isinstance(deref, BitVecRef):
                    deref = Unit(deref)
                return deref

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
                item_type = get_expr_type(expr.subtrees[0], eval_items[0])

                arr = Array(next(gen_var), IntSort(), item_type)
                arr_len = len(eval_items)
                if expr.subtrees[0].root != 'LIST_E':
                    arr_value = And([arr[i] == eval_items[i] for i in range(arr_len)])
                else:
                    arr_value = And([And(eval_items[i][0], arr[i] == eval_items[i][1]) for i in range(arr_len)])
                return arr_value, arr, item_type, arr_len

            elif expr.root == 'reverse':
                if len(expr.subtrees) == 0:
                    raise ValueError('Syntax Error: missing list argument in the function \'reverse\'')

                # ideally, there should be only one subtree.. and it should be a concrete list or a list variable
                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]

                if expr.subtrees[0].root == 'ID':
                    var_name = expr.subtrees[0].subtrees[0].root
                    arr2 = vars_dict[var_name][0]
                    arr_len = vars_dict[var_name][2]
                    item_type = arr2.range()
                elif expr.subtrees[0].root in list_types:
                    arr2 = eval_items[0][1]
                    arr_len = eval_items[0][3]
                    item_type = eval_items[0][2]
                else:
                    raise ValueError('Type Error: Expected a list in the first argument of the function \'reverse\'')

                arr = Array(next(gen_var), IntSort(), item_type)
                if expr.subtrees[0].root not in list_types:
                    arr_value = And([arr[i] == arr2[arr_len - i - 1] for i in range(arr_len)])
                else:
                    arr_value = And([eval_items[0][0]] + [arr[i] == arr2[arr_len - i - 1] for i in range(arr_len)])

                return arr_value, arr, item_type, arr_len

            elif expr.root == 'len':
                lst_eval = (eval_expr(expr.subtrees[0]))
                if isinstance(lst_eval, list):
                    return lst_eval[3]
                elif is_string(lst_eval) or is_bv(lst_eval):
                    if is_bv(lst_eval):
                        lst_eval = Unit(lst_eval)
                    return Length(lst_eval)
                elif expr.subtrees[0].root == 'ID':
                    return vars_dict[str(lst_eval)][2]
                else:
                    raise ValueError('Type Error: Expected a list or a string in the first argument of the function \'len\'')

            elif expr.root == 'append':
                if len(expr.subtrees) <= 1:
                    raise ValueError('Syntax Error: missing list argument in the function \'append\'')

                # ideally, there should be two subtree.. and it should be a concrete list or a list variable and an item
                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]
                # eval first argument: list
                if expr.subtrees[0].root == 'ID':
                    var_name = expr.subtrees[0].subtrees[0].root
                    arr2 = vars_dict[var_name][0]
                    arr_len = vars_dict[var_name][2]
                    item_type = arr2.range()
                elif expr.subtrees[0].root in list_types:
                    arr2 = eval_items[0][1]
                    arr_len = eval_items[0][3]
                    item_type = eval_items[0][2]
                else:
                    raise ValueError('Type Error: Expected a list in the first argument of the function \'append\'')

                # eval second argument: inserted_item
                if expr.subtrees[1].root == 'ID':
                    var_name = expr.subtrees[1].subtrees[0].root
                    inserted_item = vars_dict[var_name][0]
                elif expr.subtrees[1].root in list_types or type(eval_items[1]) is tuple:
                    inserted_item = eval_items[1][1]
                else:
                    inserted_item = eval_items[1]

                if arr_len > 0:
                    arr = Array(next(gen_var), IntSort(), item_type)
                else:
                    item_type = get_expr_type(expr.subtrees[1], eval_items[1])
                    arr = Array(next(gen_var), IntSort(), item_type)

                if expr.subtrees[0].root not in list_types:
                    arr_value = And([arr[arr_len] == inserted_item] + [arr[i] == arr2[i] for i in range(arr_len)])
                else:
                    arr_value = And([eval_items[0][0], arr[arr_len] == inserted_item] + [arr[i] == arr2[i] for i in range(arr_len)])

                return arr_value, arr, item_type, arr_len+1

            elif expr.root == 'remove':
                if len(expr.subtrees) == 0:
                    raise ValueError('Syntax Error: missing list argument in the function \'remove\'')

                # ideally, there should be two subtree.. and it should be a concrete list or a list variable and an item
                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]
                # eval first argument: list
                if expr.subtrees[0].root == 'ID':
                    var_name = expr.subtrees[0].subtrees[0].root
                    arr2 = vars_dict[var_name][0]
                    arr_len = vars_dict[var_name][2]
                    item_type = arr2.range()
                elif expr.subtrees[0].root in list_types:
                    arr2 = eval_items[0][1]
                    arr_len = eval_items[0][3]
                    item_type = eval_items[0][2]
                    raise ValueError('Syntax Error: missing list argument in the function \'remove\'')

                # eval second argument: removed_item
                if expr.subtrees[1].root == 'ID':
                    var_name = expr.subtrees[1].subtrees[0].root
                    removed_item = vars_dict[var_name][0]
                elif expr.subtrees[1].root in list_types:
                    removed_item = eval_items[1][1]
                else:
                    removed_item = eval_items[1]

                arr = Array(next(gen_var), IntSort(), item_type)
                # todo: edit this
                if expr.subtrees[0].root not in list_types:
                    arr_value = And([arr[arr_len] == removed_item] + [arr[i] == arr2[i] for i in range(arr_len)])
                else:
                    arr_value = And([eval_items[0][0], arr[arr_len] == removed_item] + [arr[i] == arr2[i] for i in range(arr_len)])

                return arr_value, arr, item_type, arr_len-1

            elif expr.root == 'max':
                if len(expr.subtrees) == 0:
                    raise ValueError('Syntax Error: missing integers list or two integers arguments in the function \'max\'')

                # ideally, there should be two subtree.. containing two integers
                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]
                if len(eval_items) == 1:
                    if is_array(eval_items[0]) or expr.subtrees[0].root in list_types:
                        jj = Int(next(gen_var))
                        index = Int(next(gen_var))
                        max_item = Int(next(gen_var))
                        arr = eval_items[0][1] if expr.subtrees[0].root in list_types else eval_items[0]
                        max_vc = And(Exists(index, arr[index] == max_item), ForAll(jj, max_item >= arr[jj]))
                        if expr.subtrees[0].root in list_types:
                            max_vc = And(eval_items[0][0], max_vc)
                        return max_vc, max_item
                    raise ValueError('Type Error: first argument of the function \'max\' must be of type integers list')

                if expr_is_int(expr.subtrees[0], eval_items[0]) and expr_is_int(expr.subtrees[1], eval_items[1]):
                    item1 = eval_items[0]
                    item2 = eval_items[1]
                    items_vc = None
                    if type(item1) is tuple:
                        item1 = eval_items[0][1]
                        items_vc = eval_items[0][0]
                    if type(item2) is tuple:
                        item2 = eval_items[1][1]
                        items_vc = And(items_vc, eval_items[1][0])

                    max_vc = simplify(If(item1 >= item2, item1, item2))
                    if items_vc is not None:
                        return items_vc, max_vc

                    return max_vc
                raise ValueError('Type Error: first argument of the function \'max\' must be of type integers list')

            elif expr.root == 'min':
                if len(expr.subtrees) == 0:
                    raise ValueError('Syntax Error: missing list or two integers argument in the function \'min\'')

                # ideally, there should be two subtree.. containing two integers
                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]
                if len(eval_items) == 1:
                    if is_array(eval_items[0]) or expr.subtrees[0].root in list_types:
                        jj = Int(next(gen_var))
                        index = Int(next(gen_var))
                        min_item = Int(next(gen_var))
                        arr = eval_items[0][1] if expr.subtrees[0].root in list_types else eval_items[0]
                        min_vc = And(Exists(index, arr[index] == min_item), ForAll(jj, min_item >= arr[jj]))
                        if expr.subtrees[0].root in list_types:
                            min_vc = And(eval_items[0][0], min_vc)
                        return min_vc, min_item
                    raise ValueError('Type Error: first argument of the function \'min\' must be of type integers list')

                elif expr_is_int(expr.subtrees[0], eval_items[0]) and expr_is_int(expr.subtrees[1], eval_items[1]):
                    item1 = eval_items[0]
                    item2 = eval_items[1]
                    items_vc = None
                    if type(item1) is tuple:
                        item1 = eval_items[0][1]
                        items_vc = eval_items[0][0]
                    if type(item2) is tuple:
                        item2 = eval_items[1][1]
                        items_vc = And(items_vc, eval_items[1][0])

                    min_vc = simplify(If(item1 <= item2, item1, item2))
                    if items_vc is not None:
                        return items_vc, min_vc
                    return min_vc
                raise ValueError('Type Error: Expected integers list or two integers arguments in the function \'min\'')

            elif expr.root == 'index':
                if len(expr.subtrees) <= 1:
                    raise ValueError('Syntax Error: missing arguments in the function \'index\'')

                # ideally, there should be two subtree.. and it should be a concrete list or a list variable and an item
                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]
                if expr.subtrees[0].root == 'LIST_E' or expr.subtrees[0].root == 'ID' and is_array(eval_items[0]):
                    jj = Int(next(gen_var))
                    elem_index = Int(next(gen_var))
                    arr = eval_items[0][1] if expr.subtrees[0].root == 'LIST_E' else eval_items[0]
                    item = eval_items[1]
                    item_vc = None
                    if type(eval_items[1]) is tuple:
                        item = eval_items[1][1]
                        item_vc = eval_items[1][0]
                    find_elem = Exists(jj, And(arr[jj] == item, elem_index == jj))
                    if expr.subtrees[0].root == 'LIST_E':
                        find_elem = And(eval_items[0][0], find_elem)
                    if item_vc is not None:
                        find_elem = And(item_vc, find_elem)
                    return find_elem, elem_index

                elif is_string(eval_items[0]):
                    if not (is_string(eval_items[1]) or is_bv(eval_items[1])):
                        raise ValueError(
                            'Type Error: second argument of the function \'index\' must be of type str')
                    if is_bv(eval_items[1]):
                        eval_items[1] = Unit(eval_items[1])
                    return simplify(IndexOf(eval_items[0], eval_items[1], 0))

                raise ValueError('Type Error: first argument of the function \'index\' must be of type list or string')

            elif expr.root == 'all':
                if len(expr.subtrees) == 1:
                    eval_item = eval_expr(expr.subtrees[0])
                    if is_array(eval_item) or expr.subtrees[0].root in list_types:
                        arr = eval_item[1]
                        arr_len = eval_item[3]
                        arr_vc = eval_item[0]
                    elif expr.subtrees[0].root == 'ID':
                        var_name = expr.subtrees[0].subtrees[0].root
                        arr = vars_dict[var_name][0]
                        arr_len = vars_dict[var_name][2]
                    else:
                        raise ValueError(
                            'Type Error: first argument of the function \'all\' must be of type bool list')

                    res = And([arr[i] for i in range(0, arr_len)])
                    if arr_vc is not None:
                        res = And(arr_vc, res)
                    return res
                else:
                    raise ValueError('Syntax Error: wrong number of arguments in function \'all\'')

            elif expr.root == 'any':
                if len(expr.subtrees) == 1:
                    eval_item = eval_expr(expr.subtrees[0])
                    if is_array(eval_item) or expr.subtrees[0].root in list_types:
                        arr = eval_item[1]
                        arr_len = eval_item[3]
                        arr_vc = eval_item[0]
                    elif expr.subtrees[0].root == 'ID':
                        var_name = expr.subtrees[0].subtrees[0].root
                        arr = vars_dict[var_name][0]
                        arr_len = vars_dict[var_name][2]
                    else:
                        raise ValueError(
                            'Type Error: first argument of the function \'all\' must be of type bool list')
                    res = Or([arr[i] for i in range(0, arr_len)])
                    if arr_vc is not None:
                        res = And(arr_vc, res)
                    return res
                else:
                    raise ValueError('Syntax Error: wrong number of arguments in function \'any\'')

            elif expr.root == 'charAt':
                # expects 2 arguments: a string and an index
                if len(expr.subtrees) == 2:
                    eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]
                    if is_string(eval_items[0]) and expr_is_int(expr.subtrees[1], eval_items[1]):
                        final_vc = None
                        start_index = eval_items[1]
                        if type(eval_items[1]) is tuple:
                            start_index = eval_items[1][1]
                            final_vc = eval_items[1][0]
                        if final_vc is not None:
                            return simplify(And(final_vc)), simplify(SubString(eval_items[0], start_index, 1))
                        return simplify(SubString(eval_items[0], start_index, 1))
                    raise ValueError('Type Error: the function \'charAt\' must be have 2 argument: type str, type int')

                raise ValueError('Syntax Error: wrong number of arguments in function \'charAt\'')

            elif expr.root == 'substring':
                # expects 3 arguments: a string, a starting index and an ending index
                if len(expr.subtrees) == 3:
                    eval_items = [eval_expr(expr.subtrees[jj]) for jj in range(len(expr.subtrees))]
                    if (is_string(eval_items[0]) or expr.subtrees[0].root in string_types) and expr_is_int(expr.subtrees[1], eval_items[1]) and expr_is_int(expr.subtrees[2], eval_items[2]):
                        final_vc = []
                        start_index = eval_items[1]
                        end_index = eval_items[2]
                        if type(eval_items[1]) is tuple:
                            start_index = eval_items[1][1]
                            final_vc.append(eval_items[1][0])
                        if type(eval_items[2]) is tuple:
                            end_index = eval_items[2][1]
                            final_vc.append(eval_items[2][0])
                        if final_vc:
                            return simplify(And(final_vc)), simplify(SubString(eval_items[0], start_index, end_index - start_index))
                        return simplify(SubString(eval_items[0], start_index, end_index - start_index))
                    raise ValueError('Type Error: the function \'substring\' must be have 3 argument: type str, type int, type int')

                raise ValueError('Syntax Error: wrong number of arguments in function \'substring\'')

            elif expr.root == 'LIST_COMPREHENSION':
                if len(expr.subtrees) == 3:
                    item3 = eval_expr(expr.subtrees[2])
                    if expr.subtrees[1].root == 'ID' and (is_array(item3) or expr.subtrees[2].root in list_types):
                        total_vc = []
                        if expr.subtrees[2].root in list_types:
                            comp_vc, comp_lst, comp_lst_type, arr_len = item3
                            total_vc.append(comp_vc)
                        elif expr.subtrees[2].root == 'ID':
                            arr_var_name = expr.subtrees[2].subtrees[0].root
                            comp_lst = vars_dict[arr_var_name][0]
                            comp_lst_type = comp_lst.range()
                            arr_len = vars_dict[arr_var_name][2]
                        else:
                            raise ValueError(
                                'Type Error: third argument of the list comprehension must be of type list')

                        id_backup = None
                        id_backup_tagged = None
                        var_name = expr.subtrees[1].subtrees[0].root
                        if var_name in vars_dict:
                            id_backup = vars_dict[var_name]
                            # id_backup_tagged = vars_dict[var_name + '_']
                        # as before, we assume that every list is mono-typed, i.e. it's items are of the same type
                        # item_type is the type of the items of the list comprehension
                        # first we evaluate a 'fake' expression to determine item_type in order to create a proper arr
                        tmp_var_name = next(gen_var)
                        vars_dict[var_name] = [self.create_var(comp_lst_type, tmp_var_name), comp_lst_type, 1]
                        # vars_dict[var_name + '_'] = [self.create_var(comp_lst_type, tmp_var_name + '_'), comp_lst_type, 1]
                        expr1_eval = eval_expr(expr.subtrees[0])
                        item_type = get_expr_type(expr.subtrees[0], expr1_eval)
                        arr = Array(next(gen_var), IntSort(), item_type)
                        for i in range(0, arr_len):
                            tmp_var_name = next(gen_var)
                            # warning! if the item_type is an array we may get an un-wanted behaviour since we don't
                            # know length of the array.. and it's set to 1 in the next line
                            vars_dict[var_name] = [self.create_var(comp_lst_type, tmp_var_name), comp_lst_type, 1]
                            # vars_dict[var_name + '_'] = [self.create_var(comp_lst_type, tmp_var_name + '_'), comp_lst_type, 1]
                            expr1_eval = eval_expr(expr.subtrees[0])
                            total_vc.append(comp_lst[i] == vars_dict[var_name][0])
                            if type(expr1_eval) is tuple:
                                total_vc.append(arr[i] == expr1_eval[1])
                                total_vc.append(expr1_eval[0])
                            else:
                                total_vc.append(arr[i] == expr1_eval)

                        # some dict clean up
                        if id_backup is not None:
                            vars_dict[var_name] = id_backup
                            # vars_dict[var_name + '_'] = id_backup_tagged
                        else:
                            vars_dict.pop(var_name)
                            # vars_dict.pop(var_name + '_')
                        return And(total_vc), arr, item_type, arr_len
                    else:
                        raise ValueError(
                            'Type Error: in the list comprehension: the 2nd argument must be a variable, and the 3rd argument must be of type list')
                else:
                    # we shouldn't reach here in this phase
                    raise ValueError('Syntax Error: wrong format of list comprehension')

            elif expr.root == 'sum':
                if len(expr.subtrees) == 0:
                    raise ValueError('Syntax Error: wrong number of arguments in function \'sum\'')

                # ideally, there should be two subtree.. containing two integers
                eval_items = [eval_expr(expr.subtrees[i]) for i in range(len(expr.subtrees))]
                if len(eval_items) == 1:
                    if is_array(eval_items[0]) or expr.subtrees[0].root in list_types:
                        if expr.subtrees[0].root in list_types:
                            arr, arr_len = eval_items[0][1], eval_items[0][3]
                        else:
                            arr, arr_len = eval_items[0], vars_dict[expr.subtrees[0].subtrees[0].root][2]
                        v = IntVector(next(gen_var), arr_len)
                        sum_vc = And([v[j] == arr[j] for j in range(0, arr_len)])
                        lst_sum = Sum(v)
                        if expr.subtrees[0].root in list_types:
                            sum_vc = And(eval_items[0][0], sum_vc)
                        return sum_vc, lst_sum
                    raise ValueError(
                        'Type Error: the argument of the function \'sum\' must be of type list')

                if all([expr_is_int(expr.subtrees[k], eval_items[k]) for k in range(len(expr.subtrees))]):
                    items_vc = []
                    items_num = len(expr.subtrees)
                    v = IntVector(next(gen_var), items_num)
                    for j in range(0, items_num):
                        if type(eval_items[j]) is tuple:
                            items_vc.append(v[j] == eval_items[j][1])
                            items_vc.append(eval_items[j][0])
                        else:
                            items_vc.append(v[j] == eval_items[j])
                    sum_vc = Sum(v)
                    return And(items_vc), sum_vc

                raise ValueError(
                    'Type Error: the arguments of the function \'sum\' must be of type int')

            elif expr.root == 'range':
                # warning! we only accept integer values as arguments.. i.e. no variables
                if len(expr.subtrees) == 1:
                    if expr.subtrees[0].root == 'NUM':
                        arr_len = expr.subtrees[0].subtrees[0].root
                        arr = Array(next(gen_var), IntSort(), IntSort())
                        arr_vc = And([arr[j] == j for j in range(arr_len)])
                        return arr_vc, arr, IntSort(), arr_len
                    else:
                        raise ValueError(
                            'Type Error: the argument of the function \'range\' must be of type int (only literal integers not variables)')
                elif len(expr.subtrees) == 2:
                    if expr.subtrees[0].root == 'NUM' and expr.subtrees[1].root == 'NUM':
                        start_index = expr.subtrees[0].subtrees[0].root
                        end_index = expr.subtrees[1].subtrees[0].root
                        arr = Array(next(gen_var), IntSort(), IntSort())
                        arr_vc = And([arr[j] == j for j in range(start_index, end_index)])
                        return arr_vc, arr, IntSort(), end_index - start_index
                    else:
                        raise ValueError(
                            'Type Error: the arguments of the function \'range\' must be of type int (only literal integers not variables)')
                else:
                    raise ValueError('Syntax Error: wrong number of arguments in function \'range\'')

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
                    post_loop_vars = []
                    res = construct_tr(t.subtrees[0], collected_vars=collected_vars)
                    tr_lists[1] = construct_tr(t.subtrees[1], collected_vars=collected_vars)
                    tr_lists[2] = And([vars_dict[v][0] == vars_dict[v + '_'][0] for v in vars_dict if not v.endswith('_')])
                    # print('77777777777777777777777777')
                    # print(post_loop_vars)
                    # if post_loop_vars:
                    #     tr_lists[2] = And(post_loop_vars)
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

            return eval_expr(t, collected_vars=collected_vars)
            # elif t.root in ['=', '+=', '-=', '*=', '/=', '**=', '>', '<', '>=', '<=', '==', '!=']:
            #     return eval_expr(t, collected_vars=collected_vars)
            #
            # # function call statements does not affect the program, assuming that they don't have side effects on the program variables
            # # function expressions do affect the program state.. we take care of them in eval_expr
            # elif t.root in ['INV_FUNC', 'reverse', 'len', 'append', 'remove']:
            #     return True
            #
            # return True


        vars_dict = self.vars_dict.copy()
        tr_lists = [True, [True, True], True]
        tr_lists[0] = construct_tr(ast)
        return tr_lists[0], tr_lists[1][0], tr_lists[1][1], tr_lists[2]



if __name__ == '__main__':
    input_code = read_source_file("unit_tests/test_max.py")
    # input_code = read_source_file("benchmarks/hybrid_benchmarks/test6_hybrid.py")
    # input_code = read_source_file("benchmarks/strings_benchmarks/test6_strings.py")
    # input_code = read_source_file("benchmarks/integers_benchmarks/test7_ints.py")
    pre_loop, loop_cond, loop_body, post_loop = VCGenerator()(input_code)
