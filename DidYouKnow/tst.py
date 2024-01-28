import random


class TicTacToe:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = random.choice(['X', 'O'])

    def get_winner(self):
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != ' ':
                return self.board[row][0]
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != ' ':
                return self.board[0][col]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return self.board[0][0]
        elif self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return self.board[0][2]
        return None

    def is_draw(self):
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == ' ':
                    return False
        return True

    def make_move(self, row, col):
        self.board[row][col] = self.current_player
        self.current_player = 'X' if self.current_player == 'O' else 'O'

    def play(self):
        while True:
            print_board(self.board)
            row, col = get_user_input()
            self.make_move(row, col)
            winner = self.get_winner()
            if winner is not None:
                print(f'Winner: {winner}')
                break
            if self.is_draw():
                print('Draw')
                break


def print_board(board):
    for row in board:
        print(' | '.join(row))


def get_user_input():
    row = int(input('Enter row: '))
    col = int(input('Enter column: '))
    return row, col


if __name__ == '__main__':
    tic_tac_toe = TicTacToe()
    tic_tac_toe.play()
