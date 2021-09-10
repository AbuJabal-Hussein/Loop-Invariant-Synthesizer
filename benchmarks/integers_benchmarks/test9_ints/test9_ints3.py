from utilities.inv import __inv__

x = 0
i = 0
n = 30
while i <= n:
	__inv__(x=x, i=i, n=n)
	i += 1
	x += i
