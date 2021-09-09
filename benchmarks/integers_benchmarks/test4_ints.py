from utilities.inv import __inv__, append

myList = [20, 80, 60]
n = len(myList) * 2
i = 0
while i < n:
	__inv__(myList=myList, n=n, i=i)
	myList = append(myList, i * i)
	i += 1
