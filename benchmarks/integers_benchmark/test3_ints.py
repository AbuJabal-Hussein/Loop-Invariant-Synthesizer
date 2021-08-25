from utilities.inv import __inv__
num = 59826494
count = 0

while num >= 1:
	__inv__(num=num, count=count)
	num = int(num / 10)
	count += 1
