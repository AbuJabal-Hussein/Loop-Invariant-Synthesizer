from utilities.inv import __inv__, index, reverse

myList = ['abc7d', '7efg', 'hijk7', 'lmnop77', 'qr7stuv', 'w7xyz']
newList = myList
num = len(myList) * 7 - index(myList[2], '7')
i = 0
while i < num:
	__inv__(myList=myList, newList=newList, num=num, i=i)
	newList = reverse(newList)
	if newList[0] == 'abc7d':
		i = num + 7
	i += 2
