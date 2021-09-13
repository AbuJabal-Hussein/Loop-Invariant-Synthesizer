from utilities.inv import __inv__, append
# should find trivial one
myList = []
i = 0
n = len(myList)
while i < 8:
	__inv__(myList=myList, i=i, n=n)
	myList = append(myList, i * i)
	n = len(myList)
	i += 1
