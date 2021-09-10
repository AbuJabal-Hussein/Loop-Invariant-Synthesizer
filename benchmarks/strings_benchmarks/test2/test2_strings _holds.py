from utilities.inv import __inv__, charAt, index
# count the number of digits in a string
# we want to check the property: does the string contain only digits (countDigits == len(str1))
# for this example, the condition does not hold, therefore, the synthesizer shouldn't find a proper invariant
str1 = '15689425'
countDigits = 0
strLen = len(str1)
digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
i = 0
while i < strLen:
	__inv__(str1=str1, countDigits=countDigits, strLen=strLen, digits=digits, i=i)
	if index(digits, charAt(str1, i)) != -1:
		countDigits += 1
	i += 1
if strLen < len(digits):
	i = len(digits)
else:
	i = len(digits) + 5
