from utilities.inv import __inv__

# assume mat is a square matrix
mat = [[4, 4, 3], [2, 6, 13], [9, 7, 3]]
i = 0
rowsNum = len(mat)
colsNum = len(mat[0])

while i < rowsNum:
    mat[i] = [mat[i][j] / mat[i][0] for j in [0, 1, 2]]  # consider adding range(0, colsNum)
    i += 1

if colsNum > 2:
    mat[0][2] -= 3
elif colsNum == 2:
    mat[0][1] -= 5
