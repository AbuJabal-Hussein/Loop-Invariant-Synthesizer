from utilities.inv import __inv__
# counting/bucket sort
# assumptions: the list length is 15, and the numbers are taken  from the interval [0,200)

myList = [180, 67, 155, 168, 119, 148, 70, 140, 59, 50, 25, 98, 103, 124, 114]
sortedList = [0 for i in range(15)]

count = [0 for i in range(200)]

loopnum = 0
i = 0
j = 0
arrLen = 15
while (i < arrLen) and (loopnum < 2):
    __inv__(myList=myList, sortedList=sortedList, count=count, iteration=loopnum, i=i, j=j, arrLen=arrLen)
    if loopnum == 0:
        count[myList[i]] += 1
        i += 1
    elif loopnum == 1:
        if count[j] > 0:
            sortedList[i] = j
            count[j] -= 1
            i += 1
        if count[j] == 0:
            j += 1

    if i == arrLen:
        loopnum += 1
        i = 0
