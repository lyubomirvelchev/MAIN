import unittest
from unittest.mock import patch
from tictactoe import ValidBoard, CheckWinner, Game, PLAYER_FIELDS

EMPTY_DEFAULT_BOARD = [
    [" ", " ", " "],
    [" ", " ", " "],
    [" ", " ", " "]
]


class TestTicTacToe(unittest.TestCase):

    def setUp(self):
        self.board = ValidBoard()

    def test_initial_empty_board_default_value(self):
        expected_board = EMPTY_DEFAULT_BOARD
        self.assertEqual(self.board.state, expected_board)

    def test_initial_empty_board_non_default_value(self):
        custom_board = ValidBoard(5)
        expected_board = [
            [" ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " "],
        ]
        self.assertEqual(custom_board.state, expected_board)

    def test_set_up_changes_board_state(self):
        self.board.set_value('X', (0, 0))
        expected_board = [
            ["X", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]
        self.assertEqual(self.board.state, expected_board)

    def test_invalid_value_does_not_pass_check(self):
        check_passed = self.board.is_input_valid("F", (0, 0))
        self.assertEqual(check_passed, False)

    def test_non_tuple_coords_do_not_pass_check(self):
        check_passed = self.board.is_input_valid('X', [0, 0])
        self.assertEqual(check_passed, False)

    def test_non_digit_coords_do_not_pass_check(self):
        check_passed = self.board.is_input_valid('X', ('a', 'b'))
        self.assertEqual(check_passed, False)

    def test_out_of_range_coords_do_not_pass_check(self):
        check_passed = self.board.is_input_valid('X', (3, 3))
        self.assertEqual(check_passed, False)
        negative_numbers_check_passed = self.board.is_input_valid('X', (-1, -1))
        self.assertEqual(negative_numbers_check_passed, False)

    def test_empty_field_updated_after_new_value_is_set_up(self):
        self.board.set_value('X', (0, 0))
        empty_fields = [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        self.assertEqual(self.board.empty_field_coords, empty_fields)

    def test_coords_of_already_taken_field_do_not_pass_check(self):
        self.board.set_value('X', (0, 0))
        check_passed = self.board.is_input_valid('O', (0, 0))
        self.assertEqual(check_passed, False)

    def test_empty_field_updated_after_new_value_is_set_up_on_non_default_board(self):
        custom_board = ValidBoard(5)
        custom_board.set_value('X', (0, 0))
        empty_fields = [
            (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)
        ]
        self.assertEqual(custom_board.empty_field_coords, empty_fields)


class TestCheckWinner(unittest.TestCase):
    def setUp(self):
        self.checker = CheckWinner()

    def test_empty_board_yields_no_winner(self):
        is_winner = self.checker.is_winning_board(EMPTY_DEFAULT_BOARD)
        self.assertEqual(is_winner, False)

    def test_horizontal_line_yileds_a_winner(self):
        board = [
            ["X", "X", "X"],
            [" ", " ", " "],
            [" ", " ", " "]
        ]
        is_winner = self.checker.is_winning_board(board)
        self.assertEqual(is_winner, True)

    def test_vertical_line_yields_a_winner(self):
        board = [
            ["X", " ", " "],
            ["X", " ", " "],
            ["X", " ", " "]
        ]
        is_winner = self.checker.is_winning_board(board)
        self.assertEqual(is_winner, True)

    def test_main_diagonal_line_yields_a_winner(self):
        board = [
            ["X", " ", " "],
            [" ", "X", " "],
            [" ", " ", "X"]
        ]
        is_winner = self.checker.is_winning_board(board)
        self.assertEqual(is_winner, True)

    def test_counter_diagonal_line_yields_a_winner(self):
        board = [
            [" ", " ", "X"],
            [" ", "X", " "],
            ["X", " ", " "]
        ]
        is_winner = self.checker.is_winning_board(board)
        self.assertEqual(is_winner, True)

    def test_full_board_yields_no_winner(self):
        board = [
            ["X", "X", "O"],
            ["O", "O", "X"],
            ["X", "O", "X"]
        ]
        is_winner = self.checker.is_winning_board(board)
        self.assertEqual(is_winner, False)

    def test_full_board_with_bigger_size_yields_no_winner(self):
        big_board_checker = CheckWinner(5)
        board = [
            ["X", "X", "O", "O", "X"],
            ["O", "O", "X", "X", "O"],
            ["X", "O", "X", "X", "O"],
            ["X", "O", "X", "X", "O"],
            ["X", "O", "X", "X", "O"]
        ]
        is_winner = big_board_checker.is_winning_board(board)
        self.assertEqual(is_winner, False)

    def test_half_empty_board_with_bigger_size_yields_no_winner(self):
        big_board_checker = CheckWinner(5)
        board = [
            ["X", " ", "O", "O", "X"],
            ["O", " ", "X", "X", "O"],
            ["X", " ", "X", "X", "O"],
            ["X", " ", "X", " ", "O"],
            ["X", " ", "X", " ", "O"]
        ]
        is_winner = big_board_checker.is_winning_board(board)
        self.assertEqual(is_winner, False)

    def test_board_with_bigger_size_yields_a_winner_horizontal_line(self):
        big_board_checker = CheckWinner(5)
        board = [
            ["X", "X", "O", "O", "X"],
            ["O", " ", " ", "X", "O"],
            ["X", "O", " ", "X", "O"],
            ["X", " ", "X", "X", "O"],
            ["X", "X", "X", "X", "X"]
        ]
        is_winner = big_board_checker.is_winning_board(board)
        self.assertEqual(is_winner, True)

    def test_board_with_bigger_size_yields_a_winner_vertical_line(self):
        big_board_checker = CheckWinner(5)
        board = [
            ["X", " ", " ", " ", " "],
            ["X", " ", " ", " ", " "],
            ["X", " ", " ", " ", " "],
            ["X", " ", " ", " ", " "],
            ["X", " ", " ", " ", " "]
        ]
        is_winner = big_board_checker.is_winning_board(board)
        self.assertEqual(is_winner, True)

    def test_board_with_bigger_size_yields_a_winner_main_diagonal_line(self):
        big_board_checker = CheckWinner(5)
        board = [
            ["X", " ", "O", "O", "X"],
            ["O", "X", " ", "X", "O"],
            ["X", "O", "X", "X", " "],
            [" ", "X", "X", "X", "O"],
            ["X", "O", "X", " ", "X"]
        ]
        is_winner = big_board_checker.is_winning_board(board)
        self.assertEqual(is_winner, True)

    def test_board_with_bigger_size_yields_a_winner_counter_diagonal_line(self):
        big_board_checker = CheckWinner(5)
        board = [
            ["X", " ", "O", "O", "X"],
            ["O", " ", "X", "X", "O"],
            ["X", "O", "X", "X", " "],
            [" ", "X", "X", " ", "O"],
            ["X", "O", "X", " ", "X"]
        ]
        is_winner = big_board_checker.is_winning_board(board)
        self.assertEqual(is_winner, True)


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_game_initialization(self):
        self.assertEqual(self.game.board.state, EMPTY_DEFAULT_BOARD)
        self.assertEqual(self.game.current_player, 1)

    def test_game_initialization_bigger_board(self):
        game = Game(5)
        expected_board = [
            [" ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " "]
        ]
        self.assertEqual(game.board.state, expected_board)

    @patch('builtins.input', return_value="")
    def test_coords_are_empty_strings(self, input):
        self.game.single_turn()
        self.assertEqual(self.game.board.state, EMPTY_DEFAULT_BOARD)

    @patch('builtins.input', return_value="a")
    def test_coords_are_strings(self, input):
        self.game.single_turn()
        self.assertEqual(self.game.board.state, EMPTY_DEFAULT_BOARD)

    @patch('builtins.input', side_effect=["1", "a"])
    def test_invalid_second_input(self, input):
        self.game.single_turn()
        self.assertEqual(self.game.board.state, EMPTY_DEFAULT_BOARD)

    @patch('builtins.input', side_effect=["0", "0"])
    def test_valid_input_changes_empty_board(self, input):
        expected_board = [
            ["X", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]
        self.game.single_turn()
        self.assertEqual(self.game.board.state, expected_board)

    @patch('builtins.input', side_effect=["0", "0"])
    def test_valid_input_does_not_change_board_if_field_taken(self, input):
        expected_board = [
            ["X", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]
        self.game.board.state = expected_board
        self.game.current_player = 2
        self.game.single_turn()
        self.assertEqual(self.game.board.state, expected_board)

    @patch('builtins.input', side_effect=["1", "1"])
    def test_valid_input_changes_non_empty_board(self, input):
        initial_board = [
            ["X", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]
        expected_board = [
            ["X", " ", " "],
            [" ", "O", " "],
            [" ", " ", " "]
        ]
        self.game.board.state = initial_board
        self.game.current_player = 2
        self.game.single_turn()
        self.assertEqual(self.game.board.state, expected_board)

    @patch('builtins.input', side_effect=["0", "0"])
    def test_player_swtiched_after_turn(self, input):
        self.game.single_turn()
        self.assertEqual(self.game.current_player, 2)

    @patch('builtins.input', side_effect=["7", "7"])
    def test_player_not_switched_after_invalid_turn(self, input):
        self.game.single_turn()
        self.assertEqual(self.game.current_player, 1)

    @patch('builtins.input', side_effect=["0", "0"])
    def test_no_winner_after_first_turn(self, input):
        self.game.single_turn()
        self.assertEqual(self.game.winner, None)

    @patch('builtins.input', side_effect=["0", "0"])
    def test_winner_changed_when_board_is_winning(self, input):
        self.game.board.state = [
            [" ", "X", "X"],
            [" ", "O", "O"],
            [" ", " ", " "]
        ]
        self.game.single_turn()
        self.assertEqual(self.game.winner, 1)

    def test_winner_is_none_when_board_is_full_and_game_is_draw(self):
        self.game.board.state = [
            ["X", "O", "X"],
            ["O", "X", "O"],
            ["O", "X", "O"]
        ]
        self.assertEqual(self.game.winner, None)

    def test_game_has_ended_when_a_tie_and_no_winner(self):
        checker = CheckWinner()
        moves = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (1, 1), (2, 0), (2, 2), (2, 1)]
        for idx in range(9):
            self.assertEqual(self.game.has_game_ended(), False)
            self.game.board.set_value(PLAYER_FIELDS[self.game.current_player], moves[idx])
            if checker.is_winning_board(self.game.board.state):
                self.winner = self.game.current_player
                return
            self.game.switch_player()
        self.assertEqual(self.game.winner, None)
        self.assertEqual(self.game.has_game_ended(), True)

    def test_game_has_winner_when_board_is_full(self):
        checker = CheckWinner()
        moves = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1), (2, 0), (2, 2)]
        for idx in range(9):
            self.game.board.set_value(PLAYER_FIELDS[self.game.current_player], moves[idx])
            if checker.is_winning_board(self.game.board.state):
                self.winner = self.game.current_player
                return
            self.game.switch_player()
            self.assertEqual(self.game.has_game_ended(), False)
        self.assertEqual(self.game.winner, 1)
        self.assertEqual(self.game.has_game_ended(), True)


if __name__ == "__main__":
    unittest.main()
