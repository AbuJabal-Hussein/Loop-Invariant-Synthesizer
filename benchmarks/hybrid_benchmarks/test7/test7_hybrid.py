from utilities.inv import __inv__
myList = [5, 6, 5, 9, 7, 2, 20, 6]
i = 0
num = 0
while i < len(myList):
	__inv__(i=i, myList=myList, num=num)
	num +=  myList[i]
	i += 1
