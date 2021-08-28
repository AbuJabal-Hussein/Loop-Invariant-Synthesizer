from utilities.inv import __inv__
# should create a pattern like this: ( for n = 4 )
# ****
# ***
# **
# *
n = 20
myList = [' ' for k in range(20)]
i = n - 1
str1 = ''
while i >= 0:
    __inv__(n=n, myList=myList, i=i, str1=str1)
    str1 = str1 + '*'
    myList[i] = str1
    i -= 1
