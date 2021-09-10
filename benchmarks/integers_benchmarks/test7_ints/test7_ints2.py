from utilities.inv import __inv__

# reverse num
num = 546983
revrsed_num = 0

while num != 0:
	__inv__(num=num, revrsed_num=revrsed_num)
	revrsed_num = revrsed_num * 10 + (num % 10)
	num = int(num / 10)
