from utilities.inv import __inv__
x = 0
y = 0
i = 0
n = 10
while i < n:
	__inv__(i=i, x=x, y=y, n=n)
	i += 1
	x += 2
	y += x
