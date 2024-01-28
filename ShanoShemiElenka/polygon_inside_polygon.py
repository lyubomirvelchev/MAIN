import matplotlib.pyplot as plt
import math
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import random


def calculate_line_parameters(first_point_coordinates, second_point_coordinates):
    """
        This function takes the coordinates of two points and returns the equation of the line that was defined by the
        given points.

        :param first_point_coordinates: The two coordinates of the first point that lies on a line
        :param second_point_coordinates: The two coordinates of the second point that lies on the same line
        :return: The three parameters that define line which the two given points define
    """

    x1, y1 = first_point_coordinates[0], first_point_coordinates[1]
    x2, y2 = second_point_coordinates[0], second_point_coordinates[1]
    a = y2 - y1
    b = x1 - x2
    c = (x2 - x1) * y1 - (y2 - y1) * x1
    return a, b, c


def get_intersection_point(first_line_params, second_line_params):
    """
        This function calculates where two lines intersect and returns the coordinates of the intersection point.

        :param first_line_params: The three parameter of the line equation of the first line
        :param second_line_params: The three parameter of the line equation of the second line
        :return: Coordinates of the point where the two given lines intersect
    """

    D = first_line_params[0] * second_line_params[1] - first_line_params[1] * second_line_params[0]
    Dx = -first_line_params[2] * second_line_params[1] - first_line_params[1] * -second_line_params[2]
    Dy = first_line_params[0] * -second_line_params[2] - -first_line_params[2] * second_line_params[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return False


def find_single_inside_point(coord1, coord2, coord3, space):
    """
        A single iteration of the algorithm consists of choosing three edges of the polygon that are next to each other
        and calculating the parameters of the two lines that are defined by the two sides of the polygon. Then we find
        the equation for the 4 parallel lines (two for each of the chosen sides of the polygon). Later we intersect
        those four lines and we get 4 different points. If the chosen 3 edges form an angle less than 180 degrees, than
        the only point that is inside the polygon will be the first point of the inside polygon. If the angle is bigger
        than 180, we construct the equation of the line that is defined by the middle edge (the second one) and the
        only point that is outside of the polygon. From the three points that are inside the polygon, only the correct
        one lies on the line.
    """
    parallel_line_coord1 = []
    parallel_line_coord2 = []
    parallel_line_coord3 = []
    parallel_line_coord4 = []
    x = random.uniform(1, 10)
    xx = random.uniform(1, 10)
    while x == xx:
        xx = random.uniform(1, 10)

    parameters = calculate_line_parameters(coord1, coord2)
    parameters2 = calculate_line_parameters(coord2, coord3)

    c1_prim = parameters[2] + space * math.sqrt(parameters[0] * parameters[0] + parameters[1] * parameters[1])
    c1_secont = parameters[2] - space * math.sqrt(parameters[0] * parameters[0] + parameters[1] * parameters[1])

    y = (-c1_prim - (coord2[1] - coord1[1]) * x) / (coord1[0] - coord2[0])
    yy = (-c1_prim - (coord2[1] - coord1[1]) * xx) / (coord1[0] - coord2[0])
    parallel_line_coord1.append([x, y])
    parallel_line_coord1.append([xx, yy])

    y = (-c1_secont - (coord2[1] - coord1[1]) * x) / (coord1[0] - coord2[0])
    yy = (-c1_secont - (coord2[1] - coord1[1]) * xx) / (coord1[0] - coord2[0])
    parallel_line_coord2.append([x, y])
    parallel_line_coord2.append([xx, yy])

    c2_prim = parameters2[2] + space * math.sqrt(parameters2[0] * parameters2[0] + parameters2[1] * parameters2[1])
    c2_secont = parameters2[2] - space * math.sqrt(parameters2[0] * parameters2[0] + parameters2[1] * parameters2[1])

    y = (-c2_prim - (coord3[1] - coord2[1]) * x) / (coord2[0] - coord3[0])
    yy = (-c2_prim - (coord3[1] - coord2[1]) * xx) / (coord2[0] - coord3[0])
    parallel_line_coord3.append([x, y])
    parallel_line_coord3.append([xx, yy])

    y = (-c2_secont - (coord3[1] - coord2[1]) * x) / (coord2[0] - coord3[0])
    yy = (-c2_secont - (coord3[1] - coord2[1]) * xx) / (coord2[0] - coord3[0])
    parallel_line_coord4.append([x, y])
    parallel_line_coord4.append([xx, yy])

    p1 = get_intersection_point(calculate_line_parameters(parallel_line_coord1[0], parallel_line_coord1[1]),
                                calculate_line_parameters(parallel_line_coord3[0], parallel_line_coord3[1]))

    p2 = get_intersection_point(calculate_line_parameters(parallel_line_coord2[0], parallel_line_coord2[1]),
                                calculate_line_parameters(parallel_line_coord3[0], parallel_line_coord3[1]))

    p3 = get_intersection_point(calculate_line_parameters(parallel_line_coord2[0], parallel_line_coord2[1]),
                                calculate_line_parameters(parallel_line_coord4[0], parallel_line_coord4[1]))

    p4 = get_intersection_point(calculate_line_parameters(parallel_line_coord1[0], parallel_line_coord1[1]),
                                calculate_line_parameters(parallel_line_coord4[0], parallel_line_coord4[1]))

    try:
        inside_points = []
        outside_points = []
        for coordinates in find_single_inside_point(coord[edge1], coord[edge2], coord[edge3]):
            point = Point(coordinates[0], coordinates[1])
            if polygon.contains(point):
                inside_points.append(point)
            else:
                outside_points.append(point)
        if len(inside_points) == 1:
            return inside_points[0]
        else:
            params = calculate_line_parameters([outside_points[0].x, outside_points[0].y], coord[edge2])
            for pt in inside_points:
                if abs(params[0] * pt.x + params[1] * pt.y + params[2]) < 0.01:
                    return pt
    except IndexError as exception:
        print("The current polygon does not have so many edges")
        print(exception)
        exit()

#
# def execute_single_iteration(edge1, edge2, edge3, coord):
#     """
#
#         :param edge1:
#         :param edge2:
#         :param edge3:
#         :return:
#     """
#     try:
#         inside_points = []
#         outside_points = []
#         for coordinates in find_single_inside_point(coord[edge1], coord[edge2], coord[edge3]):
#             point = Point(coordinates[0], coordinates[1])
#             if polygon.contains(point):
#                 inside_points.append(point)
#             else:
#                 outside_points.append(point)
#         if len(inside_points) == 1:
#             return inside_points[0]
#         else:
#             params = calculate_line_parameters([outside_points[0].x, outside_points[0].y], coord[edge2])
#             for pt in inside_points:
#                 if abs(params[0] * pt.x + params[1] * pt.y + params[2]) < 0.01:
#                     return pt
#     except IndexError as exception:
#         print("The current polygon does not have so many edges")
#         print(exception)
#         exit()


def execute_algoritm(coord, space_between_figures):
    """
        This function takes a polygon as parameter and

        :param coord: The coordinates of the polygon (Here we take the first coordinate as first and last element of a
                                                      list so that we can draw a beautiful figure)
        :return: The coordinates of the inside polygon
    """
    inside_coord = []
    polygon = Polygon(coord)

    number_of_edges = len(coord) - 1
    nice_points = []
    for idx in range(number_of_edges):
        if idx != number_of_edges - 1:
            nice_points.append(find_single_inside_point(coord[idx], coord[idx + 1], coord[idx + 2], space_between_figures))
        else:
            nice_points.append(find_single_inside_point(coord[idx], coord[idx + 1], coord[1], space_between_figures))

    return nice_points


polygon_coord = [[700, 400], [400, 600], [300, 400], [210, 300], [200, 100], [250, 0], [400, 400], [500, 300], [700, 400]]

nice_points = execute_algoritm(polygon_coord, 10)

xs, ys = zip(*polygon_coord)
plt.plot(xs, ys)
xs = []
ys = []
for point in nice_points:
    xs.append(point.x)
    ys.append(point.y)
xs.append(nice_points[0].x)
ys.append(nice_points[0].y)
plt.plot(xs, ys)
plt.show()
