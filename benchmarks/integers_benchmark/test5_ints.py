from utilities.inv import __inv__

myList = [1874, 4879, 4987, 6541, 154, 321, 156, 987]
count = 0
limiter = 5616
n = len(myList)
i = 0
while i < n:
	__inv__(myList=myList, count=count, limiter=limiter, n=n, i=i)
	if myList[i] > limiter:
		count += 1
	i += 1
