from utilities.inv import __inv__
# counting/bucket sort
# assumptions: the list length is 10, and the numbers are taken from the interval [0,50)

myList = [20, 6, 7, 11, 3, 33, 46, 29, 36, 39]
sortedList = [0 for i in range(10)]

count = [0 for i in range(50)]

loopnum = 0
i = 0
j = 0
while (i < 10) and (loopnum < 2):
	__inv__(myList=myList, sortedList=sortedList, count=count, loopnum=loopnum, i=i, j=j)
	if loopnum == 0:
		count[myList[i]] += 1
		i += 1
	elif loopnum == 1:
		if count[j] > 0:
			sortedList[i] = j
			count[j] -= 1
			i += 1
		if count[j] == 0:
			j += 1

	if i == 10:
		loopnum += 1
		i = 0
