import random

MIN_GRID_WIDTH, MIN_GRID_HEIGHT = 3, 3
MAX_GRID_WIDTH, MAX_GRID_HEIGHT = 10, 10


class Food:
    def __init__(self, grid):
        self.grid = grid
        self.coords = None

    def spawn_food(self):
        self.coords = random.choice(self.grid.empty_coords)
        self.grid.update_empty_coords(new_empty_coords=[], new_filled_coords=[self.coords])


class Snake:
    def __init__(self, grid, init_snake_size=3):
        self.grid = grid
        self.size = init_snake_size
        self.coords = None
        self.head = None

    def spawn_snake(self):
        row_idx = self.grid.height // 2
        self.coords = [(row_idx, col_idx) for col_idx in range(self.size)]
        self.head = self.coords[-1]
        self.grid.update_empty_coords(new_empty_coords=[], new_filled_coords=self.coords)


class Grid:
    def __init__(self, width=6, height=6):
        self.width = width
        self.height = height
        self.raise_error_if_grid_out_of_bounds()
        self.state = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.empty_coords = [(x, y) for x in range(self.width) for y in range(self.height)]
        self.snake = Snake(self)
        self.food = Food(self)

    def update_empty_coords(self, new_empty_coords, new_filled_coords):
        """Drop filled coords from empty coords and add new empty coords to empty coords."""
        self.empty_coords = [coord for coord in self.empty_coords if coord not in new_filled_coords]
        self.empty_coords.extend(new_empty_coords)

    def raise_error_if_grid_out_of_bounds(self):
        if (self.width < MIN_GRID_WIDTH
                or self.height < MIN_GRID_HEIGHT
                or self.width > MAX_GRID_WIDTH
                or self.height > MAX_GRID_HEIGHT):
            raise ValueError(f'Grid size out of bounds. Minimum size is {MIN_GRID_WIDTH}x{MIN_GRID_HEIGHT}. '
                             f'Maximum size is {MAX_GRID_WIDTH}x{MAX_GRID_HEIGHT}.')


if __name__ == '__main__':
    grid = Grid()