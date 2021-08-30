from utilities.inv import __inv__, append

myList = [20, 80, 60]
n = len(myList)
i = 0
while (i < n) and (i < 60):
	# __inv__(myList=myList, n=n, i=i)
	myList = append(myList, i * i)
	i += 1
	n = len(myList)
