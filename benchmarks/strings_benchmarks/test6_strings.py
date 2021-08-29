from utilities.inv import __inv__

myList = ['T', 'h', 'i', 's', ' ', 'i', 's', ' ', 'a', 'n', ' ', 'e', 'x', 'a', 'm', 'p', 'l', 'e']
str1 = ''
i = 0
while i < len(myList):
	__inv__(myList=myList, str1=str1, i=i)
	str1 = str1 + myList[i]
	i += 1
