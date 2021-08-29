from utilities.inv import __inv__, append, substring, charAt
# turn the string into a list such that every 2 adjacent characters form an element in the list
# in addition, rotate the list 2 characters to the right, st. if a character is alone, it must be in the end of the list

myList = []
shiftedList = []
str1 = 'abcdefghijklmnopqrstuvwxyz'
strLen = len(str1)
i = 0
while i < (strLen - 1):
	__inv__(myList=myList, shiftedList=shiftedList, str1=str1, strLen=strLen, i=i)
	myList = append(myList, substring(str1, i, i + 2))
	if i > 2:
		shiftedList = append(shiftedList, substring(str1, i - 2, i))
	i += 2
shiftedList = append(shiftedList, substring(str1, i - 2, i))
if i == strLen:
	shiftedList = append(shiftedList, substring(str1, 0, 2))
elif i == (strLen - 1):
	myList = append(myList, charAt(str1, i))
	shiftedList = append(shiftedList, charAt(str1, i) + charAt(str1, 0))
	shiftedList = append(shiftedList, charAt(str1, 1))
