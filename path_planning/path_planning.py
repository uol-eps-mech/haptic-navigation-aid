import numpy as np
from random import randint
from warnings import warn
import heapq
from path_planning.map import load_map


class Node:
    """
    A node class for A* Pathfinding
    """

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __repr__(self):
        return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    # defining less than for purposes of heap queue
    def __lt__(self, other):
        return self.f < other.f

    # defining greater than for purposes of heap queue
    def __gt__(self, other):
        return self.f > other.f


def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]


def origin_location():
    # Find the minimum x and y coord values from anchors JSON #TODO
    # hard code it for now
    min_x = 0
    min_y = 0
    x_origin = 0 - min_x
    y_origin = 0 - min_y
    return (x_origin, y_origin)


def get_goal(map, node_density):
    # TODO: will need to pull end location from Kaif's data and translate it into end node using same logic as start node
    incomplete = True
    while incomplete:
        rand_end = (int(randint(0, (len(map) - 1))*2),
                    int(randint(0, (len(map) - 1))*2))
        end = (int(rand_end[0]//node_density), int(rand_end[1]//node_density))

        if map[end[0]][end[1]] != 0:
            continue
        else:
            incomplete = False

    return end


def get_target_heading(path, node_density):
    if len(path) == 1:
        target_heading = 0
    else:
        required_movement_direction_x = node_density*(path[1][0] - path[0][0])
        required_movement_direction_y = node_density*(path[1][1] - path[0][1])
        required_movement_direction = (
            required_movement_direction_x, required_movement_direction_y)

        if required_movement_direction == (0, 1):
            target_heading = 90
        elif required_movement_direction == (1, 1):
            target_heading = 45
        elif required_movement_direction == (1, 0):
            target_heading = 0
        elif required_movement_direction == (1, -1):
            target_heading = 315
        elif required_movement_direction == (0, -1):
            target_heading = 270
        elif required_movement_direction == (-1, -1):
            target_heading = 225
        elif required_movement_direction == (-1, 0):
            target_heading = 180
        elif required_movement_direction == (-1, 1):
            target_heading = 135
    return target_heading


# TODO pull from localisation subsystem, at which point won't need map input
def get_location_and_heading(map, node_density):

    x_origin, y_origin = origin_location()

    # Replace three variables with data from localisation #TODO
    x_location = (randint(1, (len(map))/node_density)) - x_origin
    y_location = (randint(1, (len(map[0]))/node_density)) - y_origin
    heading = 0

    # Translate from global coords to nodes
    start_node_0 = len(map) - ((y_location+y_origin)*node_density)
    start_node_1 = (x_origin + x_location)*node_density - 1
    start_node = (int(round(start_node_0, 0)),
                  int(round(start_node_1, 0)))
    return (start_node, heading)


def print_map_fun(map, path, start, end):
    for step in path:
        map[step[0]][step[1]] = 2

        map[start[0]][start[1]] = 3
        map[end[0]][end[1]] = 4

    for col in map:
        line = []
        for row in col:
            if row == 1:
                line.append("\u2588"*3)
            elif row == 0:
                line.append(" . ")
            elif row == 2:
                line.append(" # ")
            elif row == 3:
                line.append(" O ")
            elif row == 4:
                line.append(" x ")
            elif row == 5:
                line.append(" L ")
        print("".join(line))


def map_angle_to_direction(heading_change):
    heading_change = round(8*(heading_change)/360, 0)
    print(heading_change)

    if heading_change == 0 or heading_change == 8 or heading_change == -8:
        turn_direction = 'N'
    elif heading_change == 1 or heading_change == -7:
        turn_direction = 'NW'
    elif heading_change == 2 or heading_change == -6:
        turn_direction = 'W'
    elif heading_change == 3 or heading_change == -5:
        turn_direction = 'SW'
    elif heading_change == 4 or heading_change == -4:
        turn_direction = 'S'
    elif heading_change == 5 or heading_change == -3:
        turn_direction = 'SE'
    elif heading_change == 6 or heading_change == -2:
        turn_direction = 'E'
    elif heading_change == 7 or heading_change == -1:
        turn_direction = 'NE'

    return (turn_direction)


def translate_path(map, path, node_density):

    x_origin, y_origin = origin_location()
    translated_path = []
    for step in path:
        translated_x = ((step[1] + 1)/node_density)-x_origin
        translated_y = ((len(map)-step[0])/node_density)-y_origin
        translated_step = (translated_x, translated_y)
        translated_path.append(translated_step)

    return (translated_path)


def astar(map, start, end, allow_diagonal_movement=True):
    """
    Returns a list of tuples as a path from the given start to the given end in the given map
    :param map:
    :param start:
    :param end:
    :return:
    """

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # heapify the open_list and Add the start node
    heapq.heapify(open_list)
    heapq.heappush(open_list, start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = 20000  # (len(map[0]) * len(map) // 2)

    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
    if allow_diagonal_movement:
        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),
                            (-1, -1), (-1, 1), (1, -1), (1, 1),)

    # Loop until you find the end
    while len(open_list) > 0:
        outer_iterations += 1

        if outer_iterations > max_iterations:
            # if we hit this point return the path such as it is
            # it will not contain the destination
            warn("giving up on pathfinding too many iterations")
            return return_path(current_node)

        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            return return_path(current_node)

        # Generate children
        children = []

        for new_position in adjacent_squares:  # Adjacent squares

            # Get node position
            node_position = (
                current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(map) - 1) or node_position[0] < 0 or node_position[1] > (len(map[0]) - 1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if map[node_position[0]][node_position[1]] != 0:
                continue

            # Check diagonal movement is valid (i.e. they don't need to walk through a wall)
            # Diagonal move
            if abs(new_position[0]) - abs(node_position[0]) != 0 and abs(new_position[1]) - abs(node_position[1]) != 0:
                left_node_x = node_position[0] - new_position[0]
                left_node_y = node_position[1]
                right_node_x = node_position[0]
                right_node_y = node_position[1] - new_position[1]

                # Check validity of nodes next to diagnonal
                if map[left_node_x][left_node_y] != 0 or map[right_node_x][right_node_y] != 0:
                    continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Create the g, h and f values
            child.h = (((child.position[0] - end_node.position[0]) ** 2) + (
                (child.position[1] - end_node.position[1]) ** 2)) ** 0.5

            if abs(child.position[0]) - abs(child.parent.position[0]) != 0 and abs(child.position[1]) - abs(child.parent.position[1]) != 0:  # Diagonal move
                child.g = current_node.g + 1.414
            else:
                child.g = current_node.g + 1

            for cell in get_one_cell_radius(child.position[0], child.position[1]):
                if map[cell[0]][cell[1]] == 0:
                    child.g += 0.5

            child.f = child.g + child.h

            # Child is already in the open list
            if len([open_node for open_node in open_list if child.position == open_node.position and child.f >= open_node.f]) > 0:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)

    warn("Couldn't get a path to destination")
    return None


def get_one_cell_radius(x, y):
    radius = [(0, 0), (0, 1), (1, 0), (1, 1), (-1, -1),
              (-1, 0), (0, -1), (1, -1), (-1, 1)]
    return [(x+elm[0], y+elm[1]) for elm in radius]


def calculate_next_direction(start, end, heading, offset, map_name, print_map=False, print_path=False):
    destination_reached = False
    env_map = load_map(map_name)
    print(env_map)

    # Define node density
    node_density = 2

    if end in get_one_cell_radius(start[0], start[1]):
        destination_reached = True
        return (None, destination_reached)

    path = astar(env_map, start, end)
    print(path)

    if print_map:
        print_map_fun(env_map, path, start, end)

    # Translate path back from nodes to location
    path = translate_path(env_map, path, node_density)

    if print_path:
        print(path)

    # heading calculations
    required_heading = get_target_heading(path, node_density)

    heading = heading + offset
    if heading >= 360:
        heading -= 360
    heading_change = required_heading - heading

    print(heading, required_heading, heading_change)

    turn_direction = map_angle_to_direction(heading_change)
    print(turn_direction)

    return (turn_direction, destination_reached)
