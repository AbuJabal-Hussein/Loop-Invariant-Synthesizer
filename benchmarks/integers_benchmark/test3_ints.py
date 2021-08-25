from utilities.inv import __inv__
myList = [1, 2, 69529, 54, 8, 99999]
num = 0
i = 1
n = len(myList)
w = 0

while i < n:
	__inv__(num=num, myList=myList, w=w, n=n, i=i)
	w = max(myList[i - 1], myList[i])
	i = i + 1
	num = max(num, w)
