from utilities.inv import __inv__
x = 16
y = 0
i = 0
while i < x:
	__inv__(i=i, x=x, y=y)
	y += x
	i += 1
