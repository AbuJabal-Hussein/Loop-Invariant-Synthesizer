from utilities.inv import __inv__
# binary search
# assume that myList is sorted in an ascending order

myList = [18, 57, 96, 103, 132, 211, 231, 295, 296, 314, 315, 400, 441, 488, 613, 636, 766, 791, 830, 863]
x = 40
low = 0
high = len(myList) - 1
mid = 0
res = -1
while low <= high and (res == -1):
	__inv__(myList=myList, x=x, low=low, high=high, mid=mid, res=res)
	mid = int((high + low) / 2)

	if myList[mid] < x:
		low = mid + 1
	elif myList[mid] > x:
		high = mid - 1
	else:
		res = mid
