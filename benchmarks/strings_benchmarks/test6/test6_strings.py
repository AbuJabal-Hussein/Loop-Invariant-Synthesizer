from utilities.inv import __inv__, charAt

myList = ['t', 'h', 'e', ' ', 'b', 'i', 'g', ' ', 's', 't', 'r', 'i', 'n', 'g']
str1 = "t"
i = 0
count = 0
while i < len(myList):
	__inv__(str1=str1, myList=myList, i=i, count=count)
	if myList[i] == str1:
		count = count + 1
	i += 1
