import math
import random
import matplotlib.pyplot as plt

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


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


def find_four_intersection_points(coord1, coord2, coord3, offset):
    """
        This function gets the coordinates of two adjacent sides of the polygo Then we calculate the four line equations
        of the four parallel lines of the two adjacent sides and we return the four intersection points of the parallel
        lines

        :param coord1: The coordinates of one of the edges of the polygon
        :param coord2: The coordinates of one of the edges of the polygon
        :param coord3: The coordinates of one of the edges of the polygon
        :param offset: The offset that will be between the two polygons
        :return: The coordinates of the four intersection points
    """

    parallel_line_coord1 = []
    parallel_line_coord2 = []
    parallel_line_coord3 = []
    parallel_line_coord4 = []

    """Here we choose two random values for x (The only condition is for them to be different numbers)"""
    x = random.uniform(1, 10)
    xx = random.uniform(1, 10)
    while x == xx:
        xx = random.uniform(1, 10)

    """Here we calculate the line equation of the two sides of the polygon and save the parameters of those equations"""
    parameters = calculate_line_parameters(coord1, coord2)
    parameters2 = calculate_line_parameters(coord2, coord3)

    """
        Here we calculate the line equation of the four parallel lines, we find two random points that lie on the
        current parallel line and save the coordinates of those lines
    """
    c1_prim = parameters[2] + offset * math.sqrt(parameters[0] * parameters[0] + parameters[1] * parameters[1])
    c1_secont = parameters[2] - offset * math.sqrt(parameters[0] * parameters[0] + parameters[1] * parameters[1])

    y = (-c1_prim - (coord2[1] - coord1[1]) * x) / (coord1[0] - coord2[0])
    yy = (-c1_prim - (coord2[1] - coord1[1]) * xx) / (coord1[0] - coord2[0])
    parallel_line_coord1.append([x, y])
    parallel_line_coord1.append([xx, yy])

    y = (-c1_secont - (coord2[1] - coord1[1]) * x) / (coord1[0] - coord2[0])
    yy = (-c1_secont - (coord2[1] - coord1[1]) * xx) / (coord1[0] - coord2[0])
    parallel_line_coord2.append([x, y])
    parallel_line_coord2.append([xx, yy])

    c2_prim = parameters2[2] + offset * math.sqrt(parameters2[0] * parameters2[0] + parameters2[1] * parameters2[1])
    c2_secont = parameters2[2] - offset * math.sqrt(parameters2[0] * parameters2[0] + parameters2[1] * parameters2[1])

    y = (-c2_prim - (coord3[1] - coord2[1]) * x) / (coord2[0] - coord3[0])
    yy = (-c2_prim - (coord3[1] - coord2[1]) * xx) / (coord2[0] - coord3[0])
    parallel_line_coord3.append([x, y])
    parallel_line_coord3.append([xx, yy])

    y = (-c2_secont - (coord3[1] - coord2[1]) * x) / (coord2[0] - coord3[0])
    yy = (-c2_secont - (coord3[1] - coord2[1]) * xx) / (coord2[0] - coord3[0])
    parallel_line_coord4.append([x, y])
    parallel_line_coord4.append([xx, yy])

    """Here we calculate the coordinates of the four points where the four parallel lines intersect"""
    p1 = get_intersection_point(calculate_line_parameters(parallel_line_coord1[0], parallel_line_coord1[1]),
                                calculate_line_parameters(parallel_line_coord3[0], parallel_line_coord3[1]))

    p2 = get_intersection_point(calculate_line_parameters(parallel_line_coord2[0], parallel_line_coord2[1]),
                                calculate_line_parameters(parallel_line_coord3[0], parallel_line_coord3[1]))

    p3 = get_intersection_point(calculate_line_parameters(parallel_line_coord2[0], parallel_line_coord2[1]),
                                calculate_line_parameters(parallel_line_coord4[0], parallel_line_coord4[1]))

    p4 = get_intersection_point(calculate_line_parameters(parallel_line_coord1[0], parallel_line_coord1[1]),
                                calculate_line_parameters(parallel_line_coord4[0], parallel_line_coord4[1]))

    return p1, p2, p3, p4


def execute_single_iteration(index1,index2,index3, coord, offset):
    """
        A single iteration of the algorithm consists of choosing three edges of the polygon that are next to each other
        and calculating the parameters of the two lines that are defined by the two sides of the polygon. Then we find
        the equation for the 4 parallel lines (two for each of the chosen sides of the polygon). Later we intersect
        those four lines and we get 4 different points. If the chosen 3 edges form an angle less than 180 degrees, than
        the only point that is inside the polygon will be the first point of the inside polygon. If the angle is bigger
        than 180, we construct the equation of the line that is defined by the middle edge (the second one) and the
        only point that is outside of the polygon. From the three points that are inside the polygon, only the correct
        one lies on the line.

        :param edge1: The index of the first edge
        :param edge2: The index of the first edge
        :param edge3: The index of the first edge
        :param coord: The coordinates of the polygon
        :param offset: The offset that will be between the two polygons
        :return:
    """
    try:
        inside_points = []
        outside_points = []
        polygon = Polygon(coord)
        for coordinates in find_four_intersection_points(coord[index1], coord[index2], coord[index3], offset):
            point = Point(coordinates[0], coordinates[1])
            if polygon.contains(point):
                inside_points.append(point)
            else:
                outside_points.append(point)
        if len(inside_points) == 1:
            return inside_points[0]
        else:
            params = calculate_line_parameters([outside_points[0].x, outside_points[0].y], coord[index2])
            for pt in inside_points:
                if abs(params[0] * pt.x + params[1] * pt.y + params[2]) < 0.01:
                    return pt
    except IndexError as exception:
        print("The current polygon does not have so many edges")
        print(exception)
        exit()


def execute_algorithm(coord, offset_between_figures=10):
    """
        This function takes a polygon as parameter and returns a new polygon that is inside the original polygon and
        a given offset

        :param offset_between_figures: The offset that will be between the two polygons
        :param coord: The coordinates of the polygon (Here we take the first coordinate as first and last element of a
                                                      list so that we can draw a beautiful figure)

        :return: The coordinates of the inside polygon
    """
    inside_coord = []

    number_of_edges = len(coord) - 1
    nice_points = []
    for idx in range(number_of_edges):
        if idx != number_of_edges - 1:
            nice_points.append(execute_single_iteration(idx, idx + 1, idx + 2, coord, offset_between_figures))
        else:
            nice_points.append(execute_single_iteration(idx, idx + 1, 1, coord, offset_between_figures))

    return nice_points


if _name_ == "_main_":
    polygon_coord = [[700, 400], [400, 600], [300, 400], [210, 300], [200, 100], [250, 0], [400, 400], [500, 300],
                     [700, 400]]

    nice_points = execute_algorithm(polygon_coord)

    """The code below this line visualises the original and the newly created polygons"""

    xs, ys = zip(*polygon_coord)
    plt.plot(xs, ys)  # original polygon

    inside_xs = []
    inside_ys = []
    for point in nice_points:
        inside_xs.append(point.x)
        inside_ys.append(point.y)
    inside_xs.append(nice_points[0].x)
    inside_ys.append(nice_points[0].y)
    plt.plot(inside_xs, inside_ys)  # new inside polygon

    plt.show()