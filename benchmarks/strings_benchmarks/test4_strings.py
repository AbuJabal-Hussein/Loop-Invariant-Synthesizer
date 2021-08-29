from utilities.inv import __inv__, charAt, append, substring

str1 = "This program converts this sentence into a list of characters"
myList = []
i = 0
strLen = len(str1)
while i < strLen:
	__inv__(str1=str1, myList=myList, i=i, strLen=strLen)
	myList = append(myList, charAt(str1, i))
	i += 1
myList = append(myList, substring(str1, 5, 12))
