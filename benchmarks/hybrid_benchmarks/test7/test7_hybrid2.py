from utilities.inv import __inv__
myList = [9, 6, 6, 9, 4, 2, 5, 6]
i = 0
num = 0
while i < len(myList):
	__inv__(i=i, myList=myList, num=num)
	num +=  myList[i]
	i += 1
