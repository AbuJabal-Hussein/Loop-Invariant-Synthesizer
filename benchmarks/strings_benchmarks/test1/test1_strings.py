from utilities.inv import __inv__, charAt
# check if string is a palindrome
str1 = 'asdfgfdsa'
strLen = len(str1)
i = 0
isPalindrome = True
while (i < int(strLen / 2)) and isPalindrome:
	__inv__(str1=str1, strLen=strLen, i=i, isPalindrome=isPalindrome)
	if charAt(str1, i) != charAt(str1, strLen - i - 1):
		isPalindrome = False
	i += 1
