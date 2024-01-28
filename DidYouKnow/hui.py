import dask

@dask.delayed
def square(x):
    return x * x

@dask.delayed
def cube(x):
    return x * x * x

numbers = [1, 2, 3, 4, 5]
squares = []
cubes = []

# Create Dask delayed objects for square and cube of each number
for number in numbers:
    squares.append(square(number))
    cubes.append(cube(number))

# Sum up all squares and cubes
total_square = dask.delayed(sum)(squares)
total_cube = dask.delayed(sum)(cubes)

# Sum up the totals
final_total = dask.delayed(lambda x, y: x + y)(total_square, total_cube)

# Perform the computation
result = final_total.compute()
print(result)  # prints 225
