from utilities.inv import __inv__
x = 60
y = 24
while y > 0:
	__inv__(x=x, y=y)
	if x > y:
		x = x - y
	else:
		y = y - x
