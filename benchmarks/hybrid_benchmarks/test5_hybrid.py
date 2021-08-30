from utilities.inv import __inv__, index
# count the number of matching characters in two strings (without duplicates)

str1 = 'asdssjkgkg84jfmnn%4k'
str2 = 'kamajsgfgk,kl%54ppreqq12!ea'
count = 0
j = 0
i = 0
while i < len(str1):
	__inv__(str1=str1, str2=str2, count=count, j=0, i=0)
	if (index(str2, str1[i]) != -1) and (j == index(str1, str1[i])):
		count += 1
	i += 1
	j += 1
