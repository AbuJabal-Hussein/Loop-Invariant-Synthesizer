from utilities.inv import __inv__, charAt

myList = ['t', 'h', 'e', ' ', 'b', 'h', 'g', ' ', 'b', 't', 'r', 'b', 'h', 'b']
str1 = "h"
i = 0
count = 0
while i < len(myList):
	__inv__(str1=str1, myList=myList, i=i, count=count)
	if myList[i] == str1:
		count = count + 1
	i += 1
