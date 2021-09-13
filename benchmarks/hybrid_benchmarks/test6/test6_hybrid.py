from utilities.inv import __inv__

myList = ["abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij", "ijk", "jkl"]
str1 = "ghi"
i = 0
j = -1
while i < len(myList):
	__inv__(myList=myList, str1=str1, i=i, j=j)
	if myList[i] == str1:
		j = i
		i = len(myList)
	else:
		i += 1
