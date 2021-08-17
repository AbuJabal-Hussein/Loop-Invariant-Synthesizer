
# string tests
st1 = 'asdasd'
st2 = 'd'
x1 = index('asdasd', 'd')
x2 = index(st1, st1)
x3 = index(st1, st2)
x4 = index(st1, 'd')
x5 = index('asdasd', st2)

# lists tests
lst = [1, 2, 3]
x = 2
n1 = index(lst, 2)
n2 = index([1, 2, 3], 2)
n3 = index(lst, x)
n4 = index(append(lst, 4), 4)
n5 = index(append(lst, 4), index('hehehohohehe', 'eho'))
n6 = index(['asd','qwe','zxc'], 'zxc')
n7 = index(lst, max(lst))
