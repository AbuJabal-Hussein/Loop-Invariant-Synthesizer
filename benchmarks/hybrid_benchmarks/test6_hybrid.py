from utilities.inv import __inv__, index

# sort a list of strings according to a list of integers
# assume that the list of integers have unique values, meaning, no 2 elements have the same value

myList = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
listOrder = [4, 6, 5, 2, 9, 0, 3, 7, 1, 8]
sortedList = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
i = 0
while i < len(myList):
	# __inv__(myList=myList, listOrder=listOrder, sortedList=sortedList, i=i)
	sortedList[i] = myList[index(listOrder, i)]
	i += 1
