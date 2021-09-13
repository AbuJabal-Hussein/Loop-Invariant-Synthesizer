from z3 import *

s_ = Int("s_")
m_ = Int("m_")
i_ = Int("i_")
i = Int("i")
s = Int("s")
m = Int("m")
len_a = Int("len_a")


a = Array('a', IntSort(), IntSort())

solver = Solver()

cond = And(i <= len_a, s <= i * m, i >= 0)
cond_ = And(i_ <= len_a, s_ <= i_ * m_)

cons1 = Implies(And(s_ == 0, i_ == 0, m_ == 0, len_a >= 0), cond_)

cons2 = Implies(And(cond, i < len_a, s_ == s + a[i], i_ == i + 1, Implies(m < a[i], m_ == a[i]), Implies(Not(m < a[i]), m_ == m)), cond_)

# cons3 = Implies(And(cond, i < len_a, s_ == s + a[i], m >= a[i], m_ == m, i_ == i + 1), cond_)

cons4 = Implies(And(cond, Not(i < len_a), s_ == s, m_ == m, i_ == i), s_ <= len_a * m_)


arr = Array('a', IntSort(), IntSort())
brr = Array('b', IntSort(), IntSort())
crr = Array('c', IntSort(), IntSort())

# statement = And(arr[0] == 1, arr[1] == 2, arr[2] == 3, brr[0] == arr[2], brr[1] == arr[1], brr[2] == arr[0])
statement = And(arr[0] == 1, arr[1] == 2, arr[2] == 3)
# solver.add(statement)

# lst_remove = And([crr[index] == arr[index] for index in range(3)])
index = 0
jj = Int('jj')
jj_ = Int('jj_')
# lst_remove = ForAll(tmp, And(Implies(tmp != 2, crr[tmp] == arr[tmp]), Implies(tmp == 2, crr[tmp] != arr[tmp])))
lst_remove = And([Implies(arr[jj] != 3, And(crr[jj] == arr[jj])) for i in range(3)])

# todo: use this to implement find:
# find_elem = Exists(jj, arr[jj] == 5)
# solver.add(And(statement, find_elem))

solver.add(And(statement, jj == jj_, lst_remove, arr[2] != crr[2]))
# solver.add(Not(And(cons1, cons2, cons4)))
# for cons in [cons1, cons2, cons3, cons4]:
#     print(cons.__str__() + ":\n")
#     solver.add(cons)
#     print(solver.check())
# solver.reset()
result = solver.check()
print(result)
ll = [2,5,2,8]
del ll[2]
print(ll)
if result == sat:
    print(solver.model())

if __name__ == '__main__':
    print('-------')
