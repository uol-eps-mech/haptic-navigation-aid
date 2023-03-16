import numpy as np
from random import randint
from warnings import warn
import heapq


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
    return path[::-1]  # Return reversed path


def get_currentlocation(maze, node_density):
    # TODO: will need to pull from Rego's data
    rand_start = (randint(0, (len(maze) - 1))*2, randint(0, (len(maze) - 1))*2)
    start = (rand_start[0]//node_density, rand_start[1]//node_density)
    return start


def get_goal(maze, node_density):
    # TODO: will need to pull from Kaif's data
    incomplete = True
    while incomplete:
        rand_end = (randint(0, (len(maze) - 1))*2,
                    randint(0, (len(maze) - 1))*2)
        end = (rand_end[0]//node_density, rand_end[1]//node_density)

        if maze[end[0]][end[1]] != 0:
            continue
        else:
            incomplete = False

    return end


def get_heading():
    heading = randint(0, 360)
    return heading


def get_heading_needed(route):
    required_movement_direction_x = route[1][0] - route[0][0]
    required_movement_direction_y = route[1][1] - route[0][1]
    required_movement_direction = (
        required_movement_direction_x, required_movement_direction_y)

    if required_movement_direction == (0, 1):
        target_heading = 0
    elif required_movement_direction == (1, 1):
        target_heading = 45
    elif required_movement_direction == (1, 0):
        target_heading = 90
    elif required_movement_direction == (1, -1):
        target_heading = 135
    elif required_movement_direction == (0, -1):
        target_heading = 180
    elif required_movement_direction == (-1, -1):
        target_heading = 225
    elif required_movement_direction == (-1, 0):
        target_heading = 270
    elif required_movement_direction == (-1, 1):
        target_heading = 315
    return target_heading


def astar(maze, start, end, allow_diagonal_movement=True):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    :param maze:
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

    # Heapify the open_list and Add the start node
    heapq.heapify(open_list)
    heapq.heappush(open_list, start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = 512  # (len(maze[0]) * len(maze) // 2)

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
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) - 1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Check diagonal movement is valid (i.e. they don't need to walk through a wall)
            if abs(new_position[0]) == abs(new_position[1]):  # Diagonal move
                left_node_x = node_position[0] - new_position[0]
                left_node_y = node_position[1]
                right_node_x = node_position[0]
                right_node_y = node_position[1] - new_position[1]

                # Check validity of nodes next to diagnonal
                if maze[left_node_x][left_node_y] != 0 or maze[right_node_x][right_node_y] != 0:
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

            # Create the f, g, and h values
            if abs(child.position[0]) == abs(child.position[1]):  # Diagonal move
                child.g = current_node.g + 1.414
            else:
                child.g = current_node.g + 1
            # child.g = current_node.g + 1 #TODO change to if statement for diagonals to be sqrt(2)

            child.h = (((child.position[0] - end_node.position[0]) **
                       2) + ((child.position[1] - end_node.position[1]) ** 2)) ** 0.5  # TODO the issue is there's a much greater bias towards h than g
            child.f = child.g + child.h

            # Child is already in the open list
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)

    warn("Couldn't get a path to destination")
    return None


def example(print_maze=True):

    maze = [[0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],]

    node_density = 2
    # start = get_currentlocation(maze)
    # end = get_goal(maze)
    # start = get_currentlocation(maze, node_density)
    # end = get_goal(maze, node_density)
    start = (0, 0)
    end = (9, 9)

    path = astar(maze, start, end)

    if print_maze:
        for step in path:
            maze[step[0]][step[1]] = 2

        maze[start[0]][start[1]] = 3
        maze[end[0]][end[1]] = 4

        for row in maze:
            line = []
            for col in row:
                if col == 1:
                    line.append("\u2588"*3)
                elif col == 0:
                    line.append(" . ")
                elif col == 2:
                    line.append(" # ")
                elif col == 3:
                    line.append(" O ")
                elif col == 4:
                    line.append(" X ")
            print("".join(line))

    return (path)


route = example()
print(route)
# heading_change = get_heading_needed(route) - get_heading()


current_heading = get_heading()
# current_heading = round(8*get_heading()/360, 0)
print("current heading is: {} ".format(current_heading))


required_heading = get_heading_needed(route)
print("desired heading is: {} ".format(required_heading))

heading_change = round(required_heading - current_heading)
# heading_change = round(8*(required_heading - current_heading)/360, 0)
print("heading change is: {} ".format(heading_change))
