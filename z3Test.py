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


solver.add(Not(And(cons1, cons2, cons4)))
# for cons in [cons1, cons2, cons3, cons4]:
#     print(cons.__str__() + ":\n")
#     solver.add(cons)
#     print(solver.check())
# solver.reset()
result = solver.check()
print(result)
if result == sat:
    print(solver.model())

