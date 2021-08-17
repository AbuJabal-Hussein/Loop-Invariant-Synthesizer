from utilities.inv import __inv__, append

i = 0
n = 5
x = 6
y = 6
myList = [4, 3, 2]#"t", "woooords", "5", "test"]

while i < n:
	__inv__(i=i, n=n, x=x, myList=myList, y=y)
	x += 1
	y = 6
	i += 1
	myList = append(myList, x)