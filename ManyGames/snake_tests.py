import unittest
from snake import Grid, Snake, Food

DEFAULT_EMPTY_GRID = [
    [' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ']
]


class TestFood(unittest.TestCase):
    def setUp(self) -> None:
        grid = Grid()
        self.food = Food(grid)

    def test_food_coords_are_in_bounds(self):
        self.food.spawn_food()
        self.assertTrue(self.food.coords[0] < 6 and self.food.coords[1] < 6)


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.grid = Grid()

    def test_initial_grid_empty(self):
        self.assertEqual(self.grid.state, DEFAULT_EMPTY_GRID)

    def test_initial_grid_empty_different_size(self):
        grid = Grid(width=5, height=3)
        expected_grid = [
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ']
        ]
        self.assertEqual(grid.state, expected_grid)

    def test_grid_minimal_boundries_not_met_exception(self):
        with self.assertRaises(ValueError):
            grid = Grid(width=1, height=1)

    def test_grid_maximal_boundries_not_met_exception(self):
        with self.assertRaises(ValueError):
            grid = Grid(width=11, height=11)

    def test_default_grid_free_coods(self):
        free_coords = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
                       (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
                       (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5)]
        self.assertEqual(self.grid.empty_coords, free_coords)

    def test_empty_coords_correctly_updated_when_snake_spawns(self):
        self.grid.snake.spawn_snake()
        for coord in self.grid.snake.coords:
            self.assertNotIn(coord, self.grid.empty_coords)

    def test_empty_coords_correctly_updated_when_food_spawns(self):
        self.grid.food.spawn_food()
        self.assertNotIn(self.grid.food.coords, self.grid.empty_coords)


class TestSnake(unittest.TestCase):
    def setUp(self):
        grid = Grid()
        self.snake = Snake(grid)

    def test_initial_snake_size(self):
        self.assertEqual(self.snake.size, 3)

    def test_snake_correctly_spawned_default_grid(self):
        self.snake.spawn_snake()
        self.assertEqual(self.snake.coords, [(3, 0), (3, 1), (3, 2)])
        self.assertEqual(self.snake.head, (3, 2))

    def test_snake_correctly_spawned_different_grid(self):
        grid = Grid(width=5, height=8)
        snake = Snake(grid)
        snake.spawn_snake()
        self.assertEqual(snake.coords, [(4, 0), (4, 1), (4, 2)])
        self.assertEqual(snake.head, (4, 2))

    def test_snake_correctly_spawned_different_grid_2(self):
        grid = Grid(width=8, height=3)
        snake = Snake(grid)
        snake.spawn_snake()
        self.assertEqual(snake.coords, [(1, 0), (1, 1), (1, 2)])
        self.assertEqual(snake.head, (1, 2))

if __name__ == '__main__':
    unittest.main()
