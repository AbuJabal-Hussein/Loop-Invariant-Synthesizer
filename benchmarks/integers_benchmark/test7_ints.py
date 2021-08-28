from utilities.inv import __inv__, append, reverse

# reverse num
num = 1234
reversed_num = 0

while num != 0:
    __inv__(num=num, reversed_num=reversed_num)
    reversed_num = reversed_num * 10 + (num % 10)
    num = int(num / 10)
