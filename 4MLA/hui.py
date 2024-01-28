import pprint


def create_empty_matrix(width, height):
    return [[0 for x in range(width)] for y in range(height)]


def primer1(n):
    B = create_empty_matrix(n, n)
    for i in range(n):
        B[i][i] = 1
    return B


def primer2(n):
    B = create_empty_matrix(n, n)
    for i in range(n):
        for j in range(0, i + 1):
            B[i][j] = 1
    return B


def sum_row_values(row1, row2, scalar):
    new_row2 = []
    for idx in range(len(row1)):
        new_row2.append(row1[idx] * scalar + row2[idx])
    return new_row2


def PRAV_HOD_NA_METODA_NA_GAUSS(A, b):
    n = len(A)
    for k in range(n - 1):
        for i in range(k + 1, n):
            l = - (A[i][k] / A[k][k])
            A[i] = sum_row_values(A[k], A[i], l)
            b[i] += b[k] * l
    return A, b


# A = [[1, 1, 1, 1], [1, 2, 2, 2], [1, 2, 3, 4], [1, 6, 8, 13]]
# b = [1, 2, 3, 4]
A = [[4, -2, 1], [-2, 4, -2], [1, -2, 4]]
b = [11, -16, 17]

pprint.pp(PRAV_HOD_NA_METODA_NA_GAUSS(A, b)[0])
pprint.pp(PRAV_HOD_NA_METODA_NA_GAUSS(A, b)[1])
