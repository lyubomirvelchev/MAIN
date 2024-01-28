board = [
    ['X', 'O', ' '],
    [' ', ' ', ' '],
    [' ', ' ', ' ']
]


col_1 = [board[0][0], board[1][0], board[2][0]]

col_2 = [board[0][1], board[1][1], board[2][1]]

col_3 = [board[0][2], board[1][2], board[2][2]]


for idx in range(3):
    col = [board[0][idx], board[1][idx], board[2][idx]]
    col_2 = [row[idx] for row in board]
    a = 0
