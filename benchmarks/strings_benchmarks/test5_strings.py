from utilities.inv import __inv__, append, substring

myList = []
shiftedList = []
str1 = 'abcdefghijklmnopqrstuvwxyz'
strLen = len(str1)
i = 0
while i < strLen - 2:
    __inv__(myList=myList, shiftedList=shiftedList, str1=str1, strLen=strLen, i=i)
    myList = append(myList, substring(str1, i, i + 2))
    if i > 2:
        shiftedList = append(shiftedList, substring(str1, i - 2, i + 2))
    i += 2
if i == strLen - 3:
    shiftedList = append(shiftedList, substring(str1, 0, 2))
elif i == strLen - 2:
    shiftedList = append(shiftedList, substring(str1, 0, 1))
