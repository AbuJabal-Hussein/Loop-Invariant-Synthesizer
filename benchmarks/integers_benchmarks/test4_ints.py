from utilities.inv import __inv__, append
# No inv in G space
myList = []
i = 0
while i < 6:
	__inv__(myList=myList, i=i)
	myList = append(myList, i * i)
	i += 1
