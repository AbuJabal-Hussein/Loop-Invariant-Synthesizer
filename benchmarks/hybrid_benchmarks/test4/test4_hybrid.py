from utilities.inv import __inv__
# There are n intermediate stations between two places A and B.
# Find the number of ways in which a train can be made to stop at x of these
# intermediate stations so that no two stopping stations are consecutive.
n = 16
x = 5
num = 1
dem = 1
s = x
loopnum = 0
t = n - s + 1
res = -1

while ((loopnum == 0) and (x != 1)) or ((loopnum == 1) and (t != (n - (2 * s) + 1))):
	__inv__(n=n, x=x, num=num, dem=dem, s=s, loopnum=loopnum, t=t, res=res)
	if loopnum == 0:
		dem *= x
		x -= 1
		if x == 1:
			loopnum += 1

	elif loopnum == 1:
		num *= t
		t -= 1
		if t == (n - (2 * s) + 1):
			loopnum += 1


if (n - s + 1) >= s:
	res = int(num / dem)
