miini = min([1, 4, 5, 2])
lst1 = [i + 7 for i in [0, 3, 7, 9, 7]]
num1 = len(lst1)
a = lst1
lst2 = [j - 1 for j in lst1]
num2 = len(lst2)
lst3 = append(lst1, 2)
num3 = len(lst3)
m = max([j - 1 for j in lst1])
has7 = any([i == 7 for i in lst1])
everything7 = all([i == 7 for i in lst1])
x = 9
hall2 = all([a == lst1, x > 4, True, False])
hany2 = any([a == lst1, x > 4, True, False])
st1 = 'asdasd'
c = charAt(st1, 2)
lstsum1 = sum([1, 2, 3, 4])
lstsum2 = sum(lst1) + 7
lstsum3 = sum([i * i for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]])
lstsum4 = sum(1, 2, 3, 4)
lstsum5 = sum(append([i * i for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]], 55))
substr1 = substring(st1, 1, 5)
substr2 = substring(substr1, 2, 3)
substr3 = substring(substring('asdasdasdasd', 3, 8), index(st1, 'd'), 3)
substr4 = charAt(substring(substr1, 1, 5), 2)

