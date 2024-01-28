PLAYER_FIELDS = {
    1: 'X',
    2: 'O'
}
INVALID_INPUT = 'Invalid input'


class PrintInterface:
    @staticmethod
    def gather_input():
        try:
            x_coord = int(input("\nPlease select row:"))
            y_coord = int(input("Please select column:"))
        except ValueError:
            return INVALID_INPUT  # the validation is handled above, here we just return a non-valid input
        return x_coord, y_coord

    @staticmethod
    def display_invalid_inputs():
        print('\nInvalid inputs\n')

    @staticmethod
    def display_board(board):
        for row in board:
            print(row)

    @staticmethod
    def display_end_game_message(winner):
        if winner:
            print(f'Player {winner} won!')
        else:
            print('Draw!')


class CheckWinner:
    def __init__(self, board_size=3):
        self.board_size = board_size

    def is_winning_board(self, board):
        return (self.check_horizontal_lines(board) or
                self.check_vertical_lines(board) or
                self.check_main_diagonal(board) or
                self.check_counter_diagonal(board)
                )

    @staticmethod
    def check_horizontal_lines(board):
        for row in board:
            if len(set(row)) == 1 and row[0] != " ":
                return True
        return False

    def check_vertical_lines(self, board):
        for col_dx in range(self.board_size):
            vertical_line_values = [row[col_dx] for row in board]
            if len(set(vertical_line_values)) == 1 and vertical_line_values[0] != " ":
                return True
        return False

    def check_main_diagonal(self, board):
        main_diagonal_fields = [board[i][i] for i in range(self.board_size)]
        if len(set(main_diagonal_fields)) == 1 and main_diagonal_fields[0] != " ":
            return True
        return False

    def check_counter_diagonal(self, board):
        counter_diagonal_fields = [board[i][self.board_size - i - 1] for i in range(self.board_size)]
        if len(set(counter_diagonal_fields)) == 1 and counter_diagonal_fields[0] != " ":
            return True
        return False


class ValidBoard:
    def __init__(self, board_size=3):
        self.state = [[" " for _ in range(board_size)] for _ in range(board_size)]
        self.empty_field_coords = [(x, y) for x in range(board_size) for y in range(board_size)]

    def set_value(self, value, coords):
        self.state[coords[0]][coords[1]] = value
        self.empty_field_coords.remove(coords)

    def is_input_valid(self, value, coords):
        if self.value_is_valid(value) and self.coord_are_valid(coords):
            return True
        return False

    @staticmethod
    def value_is_valid(value):
        if value in PLAYER_FIELDS.values():
            return True
        return False

    def coord_are_valid(self, coords):
        if coords in self.empty_field_coords:
            return True
        return False

    def display_board(self):
        for row in self.state:
            print(row)


class Game:
    def __init__(self, board_size=3):
        self.board_size = board_size
        self.current_player = 1
        self.winner = None  # 1 or 2, in case of draw it will remain None
        self.board = ValidBoard(board_size)
        self.checker = CheckWinner(board_size)
        self.interface = PrintInterface()

    def single_turn(self):
        coords = self.interface.gather_input()
        if not self.board.is_input_valid(PLAYER_FIELDS[self.current_player], coords):
            self.interface.display_invalid_inputs()
            return
        self.board.set_value(PLAYER_FIELDS[self.current_player], coords)
        self.interface.display_board(self.board.state)
        if self.checker.is_winning_board(self.board.state):
            self.winner = self.current_player
            return
        self.switch_player()

    def switch_player(self):
        self.current_player = 1 if self.current_player == 2 else 2

    def has_game_ended(self):
        if self.winner or len(self.board.empty_field_coords) == 0:
            return True
        return False

    def play(self):
        self.interface.display_board(self.board.state)
        while not self.has_game_ended():
            self.single_turn()
        self.interface.display_end_game_message(self.winner)


if __name__ == '__main__':
    current_game = Game()
    current_game.play()
