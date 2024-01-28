import matplotlib.pyplot as plt
import math
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import random

coord = [[700, 400], [400, 600], [300, 400], [210, 300], [200, 100], [700, 400]]
parallel_line_coord = []
parallel_line_coord2 = []
parallel_line_coord3 = []
parallel_line_coord4 = []

x = random.uniform(1,10)
xx = random.uniform(11,20)

def find_line_parameters(first_point_coordinates, second_point_coordinates):
    x1, y1 = first_point_coordinates[0], first_point_coordinates[1]
    x2, y2 = second_point_coordinates[0], second_point_coordinates[1]
    a = y2 - y1
    b = x1 - x2
    c = (x2 - x1) * y1 - (y2 - y1) * x1
    return a, b, c


def intersection(first_line_params, second_line_params):
    D = first_line_params[0] * second_line_params[1] - first_line_params[1] * second_line_params[0]
    Dx = -first_line_params[2] * second_line_params[1] - first_line_params[1] * -second_line_params[2]
    Dy = first_line_params[0] * -second_line_params[2] - -first_line_params[2] * second_line_params[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return False


def find_first_four_parallel_lines(coord1, coord2, coord3):
    parameters = find_line_parameters(coord1, coord2)
    parameters2 = find_line_parameters(coord2, coord3)

    c1_prim = parameters[2] + 10 * math.sqrt(parameters[0] * parameters[0] + parameters[1] * parameters[1])
    c1_secont = parameters[2] - 10 * math.sqrt(parameters[0] * parameters[0] + parameters[1] * parameters[1])

    y = (-c1_prim - (coord2[1] - coord1[1]) * x) / (coord1[0] - coord2[0])
    yy = (-c1_prim - (coord2[1] - coord1[1]) * xx) / (coord1[0] - coord2[0])
    parallel_line_coord.append([x, y])
    parallel_line_coord.append([xx, yy])

    y = (-c1_secont - (coord2[1] - coord1[1]) * x) / (coord1[0] - coord2[0])
    yy = (-c1_secont - (coord2[1] - coord1[1]) * xx) / (coord1[0] - coord2[0])
    parallel_line_coord2.append([x, y])
    parallel_line_coord2.append([xx, yy])

    c2_prim = parameters2[2] + 10 * math.sqrt(parameters2[0] * parameters2[0] + parameters2[1] * parameters2[1])
    c2_secont = parameters2[2] - 10 * math.sqrt(parameters2[0] * parameters2[0] + parameters2[1] * parameters2[1])

    y = (-c2_prim - (coord3[1] - coord2[1]) * x) / (coord2[0] - coord3[0])
    yy = (-c2_prim - (coord3[1] - coord2[1]) * xx) / (coord2[0] - coord3[0])
    parallel_line_coord3.append([x, y])
    parallel_line_coord3.append([xx, yy])

    y = (-c2_secont - (coord3[1] - coord2[1]) * x) / (coord2[0] - coord3[0])
    yy = (-c2_secont - (coord3[1] - coord2[1]) * xx) / (coord2[0] - coord3[0])
    parallel_line_coord4.append([x, y])
    parallel_line_coord4.append([xx, yy])


find_first_four_parallel_lines(coord[1], coord[2], coord[3])

xs, ys = zip(*coord)
plt.plot(xs, ys)

p1 = intersection(find_line_parameters(parallel_line_coord[0], parallel_line_coord[1]),
                  find_line_parameters(parallel_line_coord3[0], parallel_line_coord3[1]))
p2 = intersection(find_line_parameters(parallel_line_coord2[0], parallel_line_coord2[1]),
                  find_line_parameters(parallel_line_coord3[0], parallel_line_coord3[1]))
p3 = intersection(find_line_parameters(parallel_line_coord2[0], parallel_line_coord2[1]),
                  find_line_parameters(parallel_line_coord4[0], parallel_line_coord4[1]))
p4 = intersection(find_line_parameters(parallel_line_coord[0], parallel_line_coord[1]),
                  find_line_parameters(parallel_line_coord4[0], parallel_line_coord4[1]))

polygon = Polygon(coord)
counter = 0
for coordinates in [p1,p2,p3,p4]:
    point = Point(coordinates[0], coordinates[1])
    if polygon.contains(point):
        inside_point = point
        counter += 1
    if counter > 0:
        break

square = [p1,p4,p3,p2,p1]
xs,ys = zip(*square)
plt.plot(xs,ys)
plt.show()
