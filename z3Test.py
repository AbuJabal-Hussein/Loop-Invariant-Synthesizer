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

cond = And(i <= len_a, s <= i * m)
cond_ = And(i_ <= len_a, s_ <= i_ * m_)

cons1 = Implies(And(s_ == 0, i_ == 0, m_ == 0), cond_)

inner_imply = And(Implies(m < a[i], m_ == a[i]), Implies( Not(m < a[i]), m_ == m))

cons2 = Implies(And(i <= len_a, s <= i * m, i < len_a, s_ == s + a[i], i_ == i + 1, inner_imply), cond_)

cons3 = Implies(And(i <= len_a, s <= i * m, i < len_a, s_ == s + a[i], i_ == i + 1), cond_)

cons4 = Implies(And(i <= len_a, s <= i * m, Not(i < len_a), s_ == s, m_ == m, i_ == i), s_ <= len_a * m_)

solver.add(cons1, cons2, cons4, len_a == 10)
# for cons in [cons1, cons2, cons3, cons4]:
#     print(cons.__str__() + ":\n")
#     solver.add(cons)
#     print(solver.check())
# solver.reset()

print(solver.check())

print(solver.model())

