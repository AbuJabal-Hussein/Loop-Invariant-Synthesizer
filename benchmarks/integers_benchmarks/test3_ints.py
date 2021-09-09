from utilities.inv import __inv__
myList = [1, 2, 69529, 54, 8, 99999]
num = myList[0]
i = 0

while i < len(myList):
	__inv__(num=num, myList=myList, i=i)
	num = max(num, myList[i])
	i = i + 1
